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
from defs import ISSUER, LAB_RESULT_SCHEMA_ID, LAB_VACCINATION_SCHEMA_ID
from sirius_sdk.agent.aries_rfc.feature_0160_connection_protocol import *
from sirius_sdk.agent.aries_rfc.feature_0037_present_proof import *

DKMS_NAME = "indicio_test_network"


class Logger:

    async def __call__(self, *args, **kwargs):
        print(dict(**kwargs))


class Laboratory:

    def __init__(self, public_did: str):
        self.public_did = public_did
        self.lab_result_schema: sirius_sdk.Schema = None
        self.lab_result_cred_def: sirius_sdk.CredentialDefinition = None
        self.vaccination_schema: sirius_sdk.Schema = None
        self.vaccination_cred_def: sirius_sdk.CredentialDefinition = None
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
        self.lab_result_schema, self.lab_result_cred_def = await self.get_schema(LAB_RESULT_SCHEMA_ID)
        self.vaccination_schema, self.vaccination_cred_def = await self.get_schema(LAB_VACCINATION_SCHEMA_ID)

    async def generate_invitation(self):
        connection_key = await sirius_sdk.Crypto.create_key()
        inviter_endpoint = [e for e in await sirius_sdk.endpoints() if e.routing_keys == []][0]
        invitation = Invitation(
            label='IndiLynx Lab',
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
                    content="Welcome to the IndiLynx Lab!",
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
                        self_attested_data_proof_request, comment='Lab', proto_version='1.0'
                    )

    async def issue_lab_result(self, patient_did: str, results: dict):
        pairwise = await sirius_sdk.PairwiseList.load_for_did(patient_did)
        issuer = sirius_sdk.aries_rfc.Issuer(pairwise, logger=Logger(), time_to_live=600)
        preview = [sirius_sdk.aries_rfc.ProposedAttrib(key, str(value)) for key, value in results.items()]

        ok = await issuer.issue(
            values=results,
            schema=self.lab_result_schema,
            cred_def=self.lab_result_cred_def,
            preview=preview,
            comment="Here is your lab results",
            locale="en"
        )

    async def issue_vaccine(self, patient_did: str, results: dict):
        pairwise = await sirius_sdk.PairwiseList.load_for_did(patient_did)
        issuer = sirius_sdk.aries_rfc.Issuer(pairwise, logger=Logger(), time_to_live=600)
        preview = [sirius_sdk.aries_rfc.ProposedAttrib(key, str(value)) for key, value in results.items()]

        ok = await issuer.issue(
            values=results,
            schema=self.vaccination_schema,
            cred_def=self.vaccination_cred_def,
            preview=preview,
            comment="Here is your lab results",
            locale="en"
        )


def generate_random_lab_result():
    return {
        "mpid": uuid.uuid4().hex,
        "patient_local_id": uuid.uuid4().hex,
        "patient_surnames": "L.",
        "patient_given_names": "Mikhail",
        "patient_date_of_birth": random.randint(-1000000000000, 1000000000000),
        "patient_gender_legal": random.choice(["F", "M", "n/a"]),
        "patient_street_address": "Baykonurskaya",
        "patient_city": "SPb",
        "patient_state_province_region": "SPb",
        "patient_postalcode": "123456",
        "patient_country": "Russia",
        "patient_phone": 7123456789,
        "patient_email": "example@cardea.app",
        "lab_observation_date_time": int(datetime.now().timestamp()),
        "lab_specimen_collected_date": int(datetime.now().timestamp()),
        "lab_specimen_type": random.choice(["Blood", "saliva"]),
        "lab_result_status": "F",
        "lab_coding_qualifier": "LOCAL",
        "lab_code": uuid.uuid4().hex,
        "lab_description": "IndiLynx driven test lab",
        "lab_order_id": uuid.uuid4().hex,
        "lab_normality": "normal",
        "lab_result": "1",
        "lab_comment": "foo",
        "ordering_facility_id": uuid.uuid4().hex,
        "ordering_facility_id_qualifier": uuid.uuid4().hex,
        "ordering_facility_name": uuid.uuid4().hex,
        "ordering_facility_state_province_region": uuid.uuid4().hex,
        "ordering_facility_postalcode": "654321",
        "ordering_facility_country": "US",
        "performing_laboratory_id": uuid.uuid4().hex,
        "performing_laboratory_id_qualifier": uuid.uuid4().hex,
        "performing_laboratory_name": uuid.uuid4().hex,
        "performing_laboratory_state_province_region": uuid.uuid4().hex,
        "performing_laboratory_postalcode": "132435",
        "performing_laboratory_country": "Kazakhstan",
        "lab_performed_by": "dr. H.",
        "credential_issuer_name": "credential_issuer_name",
        "credential_issue_date": int(datetime.now().timestamp())
    }


def generate_random_vaccination():
    return {
        "mpid": uuid.uuid4().hex,
        "patient_local_id": uuid.uuid4().hex,
        "sending_facility": uuid.uuid4().hex,
        "patient_surnames": uuid.uuid4().hex,
        "patient_given_names": uuid.uuid4().hex,
        "patient_date_of_birth": random.randint(-1000000000000, 1000000000000),
        "patient_gender_legal": random.choice(["F", "M", "n/a"]),
        "patient_street_address": "Baykonurskaya",
        "patient_city": "SPb",
        "patient_state_province_region": "SPb",
        "patient_postalcode": "123456",
        "patient_country": "Russia",
        "patient_phone": 12345,
        "patient_email": "example@cardea.app",
        "vaccine_record_id": uuid.uuid4().hex,
        "vaccine_administration_facility_id": uuid.uuid4().hex,
        "vaccine_administration_facility_id_qualifier": uuid.uuid4().hex,
        "vaccine_administration_facility_name": uuid.uuid4().hex,
        "vaccine_administration_state_province_region": uuid.uuid4().hex,
        "vaccine_administration_postalcode": 12345,
        "vaccine_administration_country": "Russia",
        "vaccine_administration_date": int(datetime.now().timestamp()),
        "vaccine_dose_number": 2,
        "vaccine_series_complete": True,
        "vaccine_lot_number": uuid.uuid4().hex,
        "vaccine_code": uuid.uuid4().hex,
        "vaccine_code_qualifier": uuid.uuid4().hex,
        "vaccine_code_name": uuid.uuid4().hex,
        "vaccine_manufacturer_code": uuid.uuid4().hex,
        "vaccine_manufacturer_code_qualifier": uuid.uuid4().hex,
        "vaccine_manufacturer_code_name": "Sputnik V",
        "vaccine_disease_target_code": uuid.uuid4().hex,
        "vaccine_disease_target_code_qualifier": uuid.uuid4().hex,
        "vaccine_disease_target_name": uuid.uuid4().hex,
        "vaccine_administration_provider_id": uuid.uuid4().hex,
        "vaccine_administration_provider_id_qualifier": uuid.uuid4().hex,
        "vaccine_administration_provider_fullname": uuid.uuid4().hex,
        "vaccine_education_reference_material": uuid.uuid4().hex,
        "certificate_original_issuer": uuid.uuid4().hex,
        "certificate_original_identifier": uuid.uuid4().hex,
        "credential_issuer_name": uuid.uuid4().hex,
        "credential_issue_date": uuid.uuid4().hex
    }


if __name__ == '__main__':
    sirius_sdk.init(**ISSUER['SDK'])

    lab = Laboratory(public_did=ISSUER["DID"])

    asyncio.ensure_future(lab.listen())

    async def run():
        async for i, p in sirius_sdk.PairwiseList.enumerate():
            print(p.their.did)
        await lab.load_schemas()

        while True:
            case = await ainput("1 - Generate invitation \n\r"
                                "2 - Issue lab result \n\r"
                                "3 - issue vaccine \n\r"
                                "4 - Exit"
                                "Enter your option\n\r: ")
            if case == '1':
                invitation, connection_key = await lab.generate_invitation()
                qr_content = "https://demo.socialsirius.com/invitation" + invitation.invitation_url
                qr_img = qrcode.make(qr_content)
                qr_img.show()
            elif case == '2':
                results = generate_random_lab_result()
                await lab.issue_lab_result(lab.last_their_did, results)
            elif case == '3':
                results = generate_random_vaccination()
                await lab.issue_vaccine(results)
            else:
                pass

    asyncio.get_event_loop().run_until_complete(run())