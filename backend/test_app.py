import os
import tempfile
import unittest

from backend.app import create_app


class CallMeApiTest(unittest.TestCase):
    def setUp(self):
        self.database = tempfile.NamedTemporaryFile(delete=False)
        self.database.close()
        self.app = create_app({'TESTING': True, 'DATABASE': self.database.name})
        self.client = self.app.test_client()

    def tearDown(self):
        os.unlink(self.database.name)

    def test_health_and_seeded_contacts(self):
        self.assertEqual(self.client.get('/api/health').status_code, 200)
        self.assertEqual(len(self.client.get('/api/contacts').json['contacts']), 4)

    def test_create_call_and_validate_payload(self):
        response = self.client.post('/api/calls', json={'phone_number': '+15551234567'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['call']['phone_number'], '+15551234567')
        self.assertEqual(self.client.post('/api/calls', json={}).status_code, 400)

    def test_trigger_requires_e164_and_provider_configuration(self):
        invalid = self.client.post('/api/calls/trigger', json={'phone_number': '5551234567'})
        self.assertEqual(invalid.status_code, 400)
        unconfigured = self.client.post('/api/calls/trigger', json={'phone_number': '+15551234567'})
        self.assertEqual(unconfigured.status_code, 503)


if __name__ == '__main__':
    unittest.main()