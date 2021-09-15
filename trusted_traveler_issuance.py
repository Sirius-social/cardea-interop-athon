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
from defs import GOV_AGENT_CREDS, TRUSTED_TRAVELER_SCHEMA_ID, LAB_DID
from sirius_sdk.agent.aries_rfc.feature_0160_connection_protocol import *
from sirius_sdk.agent.aries_rfc.feature_0037_present_proof import *

DKMS_NAME = "indicio_test_network"


class Logger:

    async def __call__(self, *args, **kwargs):
        print(dict(**kwargs))


class Government:

    def __init__(self, public_did: str):
        self.public_did = public_did
        self.trusted_traveler_schema: sirius_sdk.Schema = None
        self.trusted_traveler_cred_def: sirius_sdk.CredentialDefinition = None

        self.last_their_did = ""
        self.require_self_attested_info = False

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

    async def load_schemas(self):
        print("loading schemas")
        self.trusted_traveler_schema, self.trusted_traveler_cred_def = await self.get_schema(TRUSTED_TRAVELER_SCHEMA_ID)

    async def generate_invitation(self):
        connection_key = await sirius_sdk.Crypto.create_key()
        inviter_endpoint = [e for e in await sirius_sdk.endpoints() if e.routing_keys == []][0]
        invitation = Invitation(
            label='IndiLynx Government Agent',
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
                self.last_their_did = pairwise.their.did

                message = sirius_sdk.aries_rfc.Message(
                    content="Welcome to the IndiLynx Government",
                    locale="en"
                )
                await sirius_sdk.send_to(message, pairwise)

                if self.require_self_attested_info:
                    self_attested_data_proof_request = {
                        "nonce": await sirius_sdk.AnonCreds.generate_nonce(),
                        "name": "Identity information request",
                        "version": "1.0",
                        "requested_attributes": {
                            "attr_address": {
                                "name": "Address"
                            },
                            "attr_given_names": {
                                "name": "Given names"
                            }
                        }
                    }

                    dkms = await sirius_sdk.ledger(DKMS_NAME)
                    machine = Verifier(prover=pairwise, ledger=dkms)
                    success = await machine.verify(
                        self_attested_data_proof_request, comment='Gov', proto_version='1.0'
                    )

                lab_data_proof_request = {
                    "nonce": await sirius_sdk.AnonCreds.generate_nonce(),
                    "name": "Laboratory information request",
                    "version": "1.0",
                    "requested_attributes": {
                        "attr_lab_result": {
                            "name": "lab_result",
                            "restrictions": {
                                "issuer_did": LAB_DID
                            }
                        }
                    },
                    # "requested_predicates": {
                    #     "lab_specimen_collected_date_predicate": {
                    #         'name': 'lab_specimen_collected_date',
                    #         'p_type': '>=',
                    #         'p_value': int(datetime.now().timestamp()) - 3*24*60*60,
                    #         "restrictions": {
                    #             "issuer_did": LAB_DID
                    #         }
                    #     }
                    # }
                }

                dkms = await sirius_sdk.ledger(DKMS_NAME)
                machine = Verifier(prover=pairwise, ledger=dkms, logger=Logger())
                success = await machine.verify(
                    lab_data_proof_request,
                    comment='Gov',
                    proto_version='1.0',
                )

                if success:
                    print(machine.requested_proof)
                    lab_result = machine.requested_proof["revealed_attrs"]["attr_lab_result"]["raw"]
                    if isinstance(lab_result, str) and (lab_result.lower() == 'negative' or lab_result == '0')\
                            or isinstance(lab_result, int) and lab_result == 0 or \
                            isinstance(lab_result, bool) and lab_result == False:
                        traveler = {
                            "traveler_surnames": "Mikhail",
                            "traveler_given_names": "L.",
                            "traveler_date_of_birth": random.randint(-1000000000000, 1000000000000),
                            "traveler_gender_legal": random.choice(["F", "M", "n/a"]),
                            "traveler_country": "Russia",
                            "traveler_origin_country": "Kazakhstan",
                            "traveler_email": "example@cardea.app",
                            "trusted_traveler_id": uuid.uuid4().hex,
                            "trusted_traveler_issue_date_time": int(datetime.now().timestamp()),
                            "trusted_traveler_expiration_date_time": int(datetime.now().timestamp())+24*60*60,
                            "governance_applied": uuid.uuid4().hex,
                            "credential_issuer_name": uuid.uuid4().hex,
                            "credential_issue_date": uuid.uuid4().hex
                        }

                        pairwise = await sirius_sdk.PairwiseList.load_for_did(self.last_their_did)
                        issuer = sirius_sdk.aries_rfc.Issuer(pairwise, logger=Logger(), time_to_live=600)
                        preview = [sirius_sdk.aries_rfc.ProposedAttrib(key, str(value)) for key, value in
                                   traveler.items()]

                        ok = await issuer.issue(
                            values=traveler,
                            schema=self.trusted_traveler_schema,
                            cred_def=self.trusted_traveler_cred_def,
                            preview=preview,
                            comment="Here is your Trusted Traveler credentials!",
                            locale="en"
                        )
                    else:
                        message = sirius_sdk.aries_rfc.Message(
                            content="Sorry, we can't issue Trusted Traveler credentials for you",
                            locale="en"
                        )
                        await sirius_sdk.send_to(message, pairwise)


if __name__ == '__main__':
    sirius_sdk.init(**GOV_AGENT_CREDS['SDK'])

    gov = Government(public_did=GOV_AGENT_CREDS["DID"])

    asyncio.ensure_future(gov.listen())

    async def run():
        await gov.load_schemas()

        while True:
            case = await ainput("1 - Generate invitation \n\r"
                                "2 - Exit\n\r"
                                "Enter your option\n\r: ")
            if case == '1':
                invitation, connection_key = await gov.generate_invitation()
                qr_content = "https://demo.socialsirius.com/invitation" + invitation.invitation_url
                qr_img = qrcode.make(qr_content)
                qr_img.show()
            elif case == '2':
                break
            else:
                pass

    asyncio.get_event_loop().run_until_complete(run())