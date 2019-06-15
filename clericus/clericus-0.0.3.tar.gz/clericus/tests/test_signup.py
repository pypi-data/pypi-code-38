import sys
sys.path.append(".")

import unittest
from aiohttp.test_utils import unittest_run_loop
from .test_case import ClericusTestCase

import faker
fake = faker.Faker()


class SignUpTestCase(ClericusTestCase):
    @unittest_run_loop
    async def testSignup(self):
        resp = await self.client.request("GET", "/me/")
        self.assertEqual(resp.status, 401)
        data = await resp.json()
        user = {
            "username": fake.name(),
            "email": fake.email(),
            "password": fake.password(),
        }

        resp = await self.client.request(
            "POST",
            "/sign-up/",
            json=user,
        )
        self.assertEqual(resp.status, 200)

        resp = await self.client.request("GET", "/me/")
        self.assertEqual(resp.status, 200)
        data = await resp.json()
        self.assertEqual(data["currentUser"]["username"], user["username"])

    @unittest_run_loop
    async def testInvalidUsername(self):
        resp = await self.client.request("GET", "/me/")
        self.assertEqual(resp.status, 401)
        data = await resp.json()
        user = {
            "username": "",
            "email": fake.email(),
            "password": fake.password(),
        }

        resp = await self.client.request(
            "POST",
            "/sign-up/",
            json=user,
        )
        self.assertEqual(resp.status, 422)
        data = await resp.json()
        self.assertEqual(len(data["errors"]), 1)

        user["username"] = 4
        resp = await self.client.request(
            "POST",
            "/sign-up/",
            json=user,
        )
        self.assertEqual(resp.status, 422)
        data = await resp.json()
        self.assertEqual(len(data["errors"]), 1)

    @unittest_run_loop
    async def testInvalidEmail(self):
        resp = await self.client.request("GET", "/me/")
        self.assertEqual(resp.status, 401)
        data = await resp.json()
        user = {
            "username": fake.name(),
            "email": "moo",
            "password": fake.password(),
        }

        resp = await self.client.request(
            "POST",
            "/sign-up/",
            json=user,
        )
        self.assertEqual(resp.status, 422)
        data = await resp.json()
        self.assertEqual(len(data["errors"]), 1)

        user["email"] = 5
        resp = await self.client.request(
            "POST",
            "/sign-up/",
            json=user,
        )
        self.assertEqual(resp.status, 422)
        data = await resp.json()
        self.assertEqual(len(data["errors"]), 1)

    @unittest_run_loop
    async def testDuplicateUsernameSignup(self):
        resp = await self.client.request("GET", "/me/")
        self.assertEqual(resp.status, 401)
        data = await resp.json()
        user = {
            "username": fake.name().lower(),
            "email": fake.email(),
            "password": fake.password(),
        }

        resp = await self.client.request(
            "POST",
            "/sign-up/",
            json=user,
        )
        self.assertEqual(resp.status, 200)

        resp = await self.client.request("GET", "/me/")
        self.assertEqual(resp.status, 200)
        data = await resp.json()
        self.assertEqual(data["currentUser"]["username"], user["username"])

        user["email"] = fake.email()
        resp = await self.client.request(
            "POST",
            "/sign-up/",
            json=user,
        )
        self.assertEqual(resp.status, 422)
        data = await resp.json()
        self.assertEqual(len(data["errors"]), 1)

        # Test case insensitive matching
        user["username"] = user["username"].upper()
        user["email"] = fake.email()
        resp = await self.client.request(
            "POST",
            "/sign-up/",
            json=user,
        )
        self.assertEqual(resp.status, 422)
        data = await resp.json()
        self.assertEqual(len(data["errors"]), 1)

        # Test with space
        user["username"] = "  " + user["username"] + "  "
        user["email"] = fake.email()
        resp = await self.client.request(
            "POST",
            "/sign-up/",
            json=user,
        )
        self.assertEqual(resp.status, 422)
        data = await resp.json()
        self.assertEqual(len(data["errors"]), 1)

    @unittest_run_loop
    async def testDuplicateEmailSignup(self):
        resp = await self.client.request("GET", "/me/")
        self.assertEqual(resp.status, 401)
        data = await resp.json()
        user = {
            "username": fake.name(),
            "email": fake.email().lower(),
            "password": fake.password(),
        }

        resp = await self.client.request(
            "POST",
            "/sign-up/",
            json=user,
        )
        self.assertEqual(resp.status, 200)

        resp = await self.client.request("GET", "/me/")
        self.assertEqual(resp.status, 200)
        data = await resp.json()
        self.assertEqual(data["currentUser"]["username"], user["username"])

        user["username"] = fake.name()
        resp = await self.client.request(
            "POST",
            "/sign-up/",
            json=user,
        )
        self.assertEqual(resp.status, 422)
        data = await resp.json()
        self.assertEqual(len(data["errors"]), 1)

        # Test case insensitive matching
        user["email"] = user["email"].upper()
        user["username"] = fake.name()
        resp = await self.client.request(
            "POST",
            "/sign-up/",
            json=user,
        )
        self.assertEqual(resp.status, 422)
        data = await resp.json()
        self.assertEqual(len(data["errors"]), 1)

        # Test with space
        user["email"] = "    " + user["email"] + "   "
        user["username"] = fake.name()
        resp = await self.client.request(
            "POST",
            "/sign-up/",
            json=user,
        )
        self.assertEqual(resp.status, 422)
        data = await resp.json()
        self.assertEqual(len(data["errors"]), 1)


if __name__ == '__main__':
    unittest.main()