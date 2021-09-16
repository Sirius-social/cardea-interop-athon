import json
import asyncio

import sirius_sdk
from defs import ISSUER, VERIFIER, HOLDER, LAB, GOV, SCHEMA_IDS


async def check_health():
    print('========= ISSUER ==========')
    async with sirius_sdk.context(**ISSUER['SDK']):
        meta = await sirius_sdk.DID.get_my_did_with_meta(ISSUER['DID'])
        assert meta['verkey'] == ISSUER['VERKEY']
        dkms = await sirius_sdk.ledger('indicio_test_network')
        # See all: https://github.com/thecardeaproject/cardea/tree/main/schemas
        for schema_id in SCHEMA_IDS:
            print(f'\n>Schema: {schema_id}')
            schema = await dkms.load_schema(schema_id, ISSUER['DID'])
            print(json.dumps(schema.body, indent=2, sort_keys=True))

    print('========= VERIFIER ==========')
    async with sirius_sdk.context(**VERIFIER['SDK']):
        meta = await sirius_sdk.DID.get_my_did_with_meta(VERIFIER['DID'])
        assert meta['verkey'] == VERIFIER['VERKEY']
        dkms = await sirius_sdk.ledger('indicio_test_network')
        # See all: https://github.com/thecardeaproject/cardea/tree/main/schemas
        for schema_id in SCHEMA_IDS:
            print(f'\n>Schema: {schema_id}')
            schema = await dkms.load_schema(schema_id, ISSUER['DID'])
            print(json.dumps(schema.body, indent=2, sort_keys=True))
    print('========= HOLDER ==========')
    async with sirius_sdk.context(**HOLDER['SDK']):
        meta = await sirius_sdk.DID.get_my_did_with_meta(HOLDER['DID'])
        assert meta['verkey'] == HOLDER['VERKEY']
        dkms = await sirius_sdk.ledger('indicio_test_network')
        # See all: https://github.com/thecardeaproject/cardea/tree/main/schemas
        for schema_id in SCHEMA_IDS:
            print(f'\n>Schema: {schema_id}')
            schema = await dkms.load_schema(schema_id, HOLDER['DID'])
            print(json.dumps(schema.body, indent=2, sort_keys=True))
    print('========= LAB ==========')
    async with sirius_sdk.context(**LAB['SDK']):
        meta = await sirius_sdk.DID.get_my_did_with_meta(LAB['DID'])
        assert meta['verkey'] == LAB['VERKEY']
        dkms = await sirius_sdk.ledger('indicio_test_network')
        # See all: https://github.com/thecardeaproject/cardea/tree/main/schemas
        for schema_id in SCHEMA_IDS:
            print(f'\n>Schema: {schema_id}')
            schema = await dkms.load_schema(schema_id, LAB['DID'])
            print(json.dumps(schema.body, indent=2, sort_keys=True))
    print('========= GOV ==========')
    async with sirius_sdk.context(**GOV['SDK']):
        dids = await sirius_sdk.DID.list_my_dids_with_meta()
        meta = await sirius_sdk.DID.get_my_did_with_meta(GOV['DID'])
        assert meta['verkey'] == GOV['VERKEY']
        dkms = await sirius_sdk.ledger('indicio_test_network')
        # See all: https://github.com/thecardeaproject/cardea/tree/main/schemas
        for schema_id in SCHEMA_IDS:
            print(f'\n>Schema: {schema_id}')
            schema = await dkms.load_schema(schema_id, GOV['DID'])
            print(json.dumps(schema.body, indent=2, sort_keys=True))


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(check_health())
