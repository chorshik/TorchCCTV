import sys
import os
from typing import Union
import shutil

from zmq.auth.asyncio import AsyncioAuthenticator
import zmq.auth


def gen_certificates(keys: [], name: str):
    pub_key, secret_key= None, None
    pub_file, secret_file = zmq.auth.create_certificates(
        keys[0], name
    )

    for key_file in os.listdir(keys[0]):
        if key_file.endswith(".key"):
            shutil.move(
                os.path.join(keys[0], key_file), os.path.join(keys[1], '.')
            )

    for key_file in os.listdir(keys[0]):
        if key_file.endswith(".key_secret"):
            shutil.move(
                os.path.join(keys[0], key_file), os.path.join(keys[2], '.')
            )
            secret_key = os.path.join(keys[2], key_file)

    load_keys = zmq.auth.load_certificate(secret_key)

    return load_keys[0], load_keys[1]


def get_keys(keys: [], type_key: str, name: str, pub_srv_key):
    if type_key == 'secret':
        try:
            server_secret_file = f"{keys[2]}/{name}.key_secret"
            print(f"Hostname:{None}, secret_srv_key:{server_secret_file}")
            load_keys = zmq.auth.load_certificate(server_secret_file)
            print()
            return load_keys[0], load_keys[1]
        except IOError as e:
            return gen_certificates(keys, name)

    elif type_key == 'public':
        server_public_file = keys[1]/f"{pub_srv_key}.key"
        print(server_public_file)
        print(f"Hostname:{None}, pub_srv_key:{server_public_file}")
        load_keys = zmq.auth.load_certificate(server_public_file)
        return load_keys[0], load_keys[1]


def get_keys_dir(path):
    base_dir = path
    keys_dir = base_dir / 'certificates'
    public_keys_dir = base_dir / 'public_keys'
    secret_keys_dir = base_dir / 'private_keys'

    if (
            not keys_dir.is_dir()
            or not public_keys_dir.is_dir()
            or not secret_keys_dir.is_dir()
    ):
        print(f'Certificates are missing')
        sys.exit(1)

    return keys_dir, public_keys_dir, secret_keys_dir


def auth(context, path):
    keys_dir, public_keys_dir, secret_keys_dir = get_keys_dir(path)

    ctx = context

    auth = AsyncioAuthenticator(context=ctx)

    # Tell authenticator to use the certificate in a directory
    auth.configure_curve(domain='*', location=public_keys_dir)
    auth.allow('127.0.0.1')
    auth.start()

    return auth, keys_dir, public_keys_dir, secret_keys_dir

