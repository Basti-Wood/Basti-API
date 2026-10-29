import ast
import asyncio
import importlib.util
import inspect
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from typing import Optional
from unittest.mock import Mock, patch


ROOT = Path(__file__).resolve().parents[1]


class MediaMetadataTests(unittest.TestCase):
    def setUp(self):
        # Do not read env files or call external APIs. Only the real queue
        # functions are imported; all persisted data lives in a temporary dir.
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        dotenv = types.SimpleNamespace(load_dotenv=Mock())
        self.requests = types.SimpleNamespace(get=Mock())
        spec = importlib.util.spec_from_file_location('media_under_test', ROOT / 'Media_share/mediashare.py')
        self.media = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {'dotenv': dotenv, 'requests': self.requests}):
            spec.loader.exec_module(self.media)
        self.media.MEDIA_FILE = Path(self.directory.name) / 'media.json'

    def stored(self):
        return self.media.get_all_media('alice')

    def test_top_submission_preserves_filename_platform_and_media_url(self):
        name = 'A & B #1 + 50%.mp3'
        url = '/api/local-media/alice/A%20%26%20B%20%231%20%2B%2050%25.mp3'
        self.media.set_media_top('alice', 'USalice', url, song_name=name, platform='local')
        self.assertEqual(self.stored()[0], {
            'Platform': 'local', 'song_name': name, 'media': url, 'username': 'USalice', 'owner_song': True
        })
        self.requests.get.assert_not_called()

    def test_legacy_local_urls_fall_back_to_the_decoded_filename(self):
        for submit in [self.media.set_media, self.media.set_media_top]:
            submit('alice', 'USalice', '/api/local-media/alice/Music/Track%20%231%20%25.mp3')
        self.assertTrue(all(item['song_name'] == 'Track #1 %.mp3' for item in self.stored()))
        self.assertTrue(all(item['Platform'] == 'local' for item in self.stored()))

    def test_supplied_youtube_titles_do_not_need_an_api_key_or_lookup(self):
        self.media.set_media_top('alice', 'USalice', 'https://youtu.be/AAAAAAAAAAA', song_name='Saved playlist title', platform='youtube')
        self.assertEqual(self.stored()[0]['song_name'], 'Saved playlist title')
        self.requests.get.assert_not_called()

    def test_legacy_youtube_clients_keep_title_resolution(self):
        self.requests.get.return_value = types.SimpleNamespace(status_code=200, json=lambda: {'items': [{'snippet': {'title': 'Resolved title'}}]})
        with patch.object(self.media, '_youtube_api_key', return_value='fake-key'):
            self.media.set_media('alice', 'viewer', 'https://youtu.be/AAAAAAAAAAA')
        self.assertEqual(self.stored()[0]['song_name'], 'Resolved title')
        self.assertEqual(self.stored()[0]['Platform'], 'youtube')
        self.requests.get.assert_called_once()

    def test_top_and_append_still_keep_order_and_owner_markers(self):
        self.media.set_media('alice', 'one', '/api/local-media/alice/One.mp3')
        self.media.set_media('alice', 'two', '/api/local-media/alice/Two.mp3')
        self.media.set_media_top('alice', 'USalice', '/api/local-media/alice/Top.mp3')
        self.assertEqual([item['song_name'] for item in self.stored()], ['Top.mp3', 'One.mp3', 'Two.mp3'])
        self.assertTrue(self.stored()[0]['owner_song'])
        self.assertNotIn('owner_song', self.stored()[1])
        self.media.set_media('bob', 'other', 'plain media')
        self.assertEqual(self.media.get_all_media('bob')[0]['song_name'], 'Unknown')

    def route(self, name):
        # Compile the actual async route in isolation from unrelated reaction/
        # LLM services. Exercise metadata forwarding and broadcast ordering.
        module = ast.parse((ROOT / 'Entrypoint.py').read_text())
        node = next(item for item in module.body if isinstance(item, ast.AsyncFunctionDef) and item.name == name)
        node.decorator_list = []
        self.updates = []

        async def push_update(owner):
            self.updates.append(self.media.get_all_media(owner))

        namespace = {
            'Optional': Optional,
            'store_media': self.media.set_media,
            'store_media_top': self.media.set_media_top,
            'media_socket_manager': types.SimpleNamespace(push_update=push_update),
        }
        isolated = ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[]))
        exec(compile(isolated, 'Entrypoint.py', 'exec'), namespace)
        return namespace[name]

    def test_routes_forward_optional_metadata_before_broadcasting(self):
        for name in ['set_media_route', 'set_media_top_route']:
            route = self.route(name)
            self.assertIsNone(inspect.signature(route).parameters['song_name'].default)
            asyncio.run(route('alice', 'USalice', '/api/local-media/alice/Stored.mp3', song_name='Original name.mp3', platform='local'))
            self.assertEqual(self.updates[-1][0 if name.endswith('top_route') else -1]['song_name'], 'Original name.mp3')

    def test_routes_still_accept_the_original_three_arguments(self):
        for name in ['set_media_route', 'set_media_top_route']:
            route = self.route(name)
            result = asyncio.run(route('alice', 'USalice', '/api/local-media/alice/Legacy.mp3'))
            self.assertIn('message', result)
            self.assertEqual(self.updates[-1][0]['song_name'], 'Legacy.mp3')


if __name__ == '__main__':
    unittest.main()
