import json
import asyncio

import sirius_sdk
from defs import ISSUER, LAB_RESULT_SCHEMA_ID


async def get_schema(schema_id: str, dkms_name: str) -> (sirius_sdk.Schema, sirius_sdk.CredentialDefinition):
    async with sirius_sdk.context(**ISSUER['SDK']):
        dkms = await sirius_sdk.ledger(dkms_name)

        request = await dkms._api.build_get_txn_author_agreement_request(submitter_did=ISSUER['DID'])
        signed = await dkms._api.sign_request(ISSUER['DID'], request)
        resp = await dkms._api.submit_request(dkms.name, signed)

        # request = await  dkms._api.build_get_acceptance_mechanisms_request(ISSUER['DID'], None, None)
        # signed = await dkms._api.sign_request(ISSUER['DID'], request)
        # resp = await dkms._api.submit_request(dkms.name, signed)

        schema = await dkms.load_schema(schema_id, ISSUER['DID'])
        cred_defs = await dkms.fetch_cred_defs()
        cred_defs = [cred_def for cred_def in cred_defs if cred_def.schema.id == schema.id]
        if len(cred_defs) > 0:
            cred_def = cred_defs[0]
        else:
            ok, cred_def = await dkms.register_cred_def(
                cred_def=sirius_sdk.CredentialDefinition(tag='TAG', schema=schema),
                submitter_did=ISSUER['DID']
            )
        return schema, cred_def


async def run():
    schema, cred_def = await get_schema(LAB_RESULT_SCHEMA_ID, "indicio_test_network")



if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(run())
