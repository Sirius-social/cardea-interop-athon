import json
import asyncio
import uuid
import random
from datetime import datetime

import aioconsole as aioconsole
import qrcode
from PIL import Image
from aioconsole import ainput

import sirius_sdk
from defs import VERIFIER_AGENT_CREDS, GOV_DID
from sirius_sdk.agent.aries_rfc.feature_0160_connection_protocol import *
from sirius_sdk.agent.aries_rfc.feature_0037_present_proof import *

DKMS_NAME = "indicio_test_network"


class Logger:

    async def __call__(self, *args, **kwargs):
        print(dict(**kwargs))


class Restaurant:

    def __init__(self, public_did: str):
        self.public_did = public_did
        self.trusted_traveler_schema: sirius_sdk.Schema = None
        self.trusted_traveler_cred_def: sirius_sdk.CredentialDefinition = None

    async def get_schema(self, schema_id: str) -> (sirius_sdk.Schema, sirius_sdk.CredentialDefinition):
        dkms = await sirius_sdk.ledger(DKMS_NAME)
        dkms.acceptance_mechanism = "service_agreement"

        schema = await dkms.load_schema(schema_id, self.public_did)
        cred_defs = await dkms.fetch_cred_defs()
        cred_defs = [cred_def for cred_def in cred_defs if cred_def.schema.id == schema.id]
        if len(cred_defs) > 0:
            cred_def = cred_defs[0]
        else:
            ok, cred_def = await dkms.register_cred_def(
                cred_def=sirius_sdk.CredentialDefinition(tag='TAG', schema=schema),
                submitter_did=self.public_did
            )
        return schema, cred_def

    async def generate_invitation(self):
        connection_key = await sirius_sdk.Crypto.create_key()
        inviter_endpoint = [e for e in await sirius_sdk.endpoints() if e.routing_keys == []][0]
        invitation = Invitation(
            label='IndiLynx Verifier',
            endpoint=inviter_endpoint.address,
            recipient_keys=[connection_key]
        )
        return invitation, connection_key

    async def listen(self):
        my_did, my_verkey = await sirius_sdk.DID.create_and_store_my_did()
        me = sirius_sdk.Pairwise.Me(did=my_did, verkey=my_verkey)
        inviter_endpoint = [e for e in await sirius_sdk.endpoints() if e.routing_keys == []][0]
        listener = await sirius_sdk.subscribe()
        print("start listening...")
        async for event in listener:
            print(dict(event))
            request = event['message']
            if isinstance(request, ConnRequest):
                connection_key = event['recipient_verkey']
                inviter_machine = Inviter(
                    me=me,
                    connection_key=connection_key,
                    my_endpoint=inviter_endpoint,
                    logger=Logger()
                )
                ok, pairwise = await inviter_machine.create_connection(request)
                await sirius_sdk.PairwiseList.ensure_exists(pairwise)

                message = sirius_sdk.aries_rfc.Message(
                    content="Welcome to the IndiLynx Verifier",
                    locale="en"
                )
                await sirius_sdk.send_to(message, pairwise)

                trusted_traveler_proof_request = {
                    "nonce": await sirius_sdk.AnonCreds.generate_nonce(),
                    "name": "Trusted traveler  request",
                    "version": "1.0",
                    "requested_attributes": {
                        "attr_lab_specimen_collected_date": {
                            'name': 'trusted_traveler_expiration_date_time',
                            # "restrictions": {
                            #     "issuer_did": GOV_DID
                            # }
                        }
                    }
                }

                dkms = await sirius_sdk.ledger(DKMS_NAME)
                machine = Verifier(prover=pairwise, ledger=dkms)
                success = await machine.verify(
                    trusted_traveler_proof_request, comment='Restaurant', proto_version='1.0'
                )

                if success:
                    message = sirius_sdk.aries_rfc.Message(
                        content="Welcome to the IndiLynx Restaurant!",
                        locale="en"
                    )
                    await sirius_sdk.send_to(message, pairwise)


if __name__ == '__main__':
    sirius_sdk.init(**VERIFIER_AGENT_CREDS['SDK'])

    restaurant = Restaurant(public_did=VERIFIER_AGENT_CREDS["DID"])

    asyncio.ensure_future(restaurant.listen())

    async def run():
        while True:
            case = await ainput("1 - Generate invitation \n\r"
                                "2 - Exit\n\r"
                                "Enter your option\n\r: ")
            if case == '1':
                invitation, connection_key = await restaurant.generate_invitation()
                qr_content = "https://demo.socialsirius.com/invitation" + invitation.invitation_url
                qr_img = qrcode.make(qr_content)
                qr_img.show()
            elif case == '2':
                break
            else:
                pass

    asyncio.get_event_loop().run_until_complete(run())