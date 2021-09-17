import sirius_sdk
import asyncio
from sirius_sdk.agent.aries_rfc.feature_0160_connection_protocol import *
from sirius_sdk.errors.indy_exceptions import AnoncredsMasterSecretDuplicateNameError
import json

from PIL import Image
from pyzbar.pyzbar import decode
import base64

from defs import HOLDER


class Logger:

    async def __call__(self, *args, **kwargs):
        print(dict(**kwargs))


PROVER_SECRET_ID = 'prover-secret-id'
from aioconsole import ainput


async def run():

    # Ensure master-secret exists
    try:
        await sirius_sdk.AnonCreds.prover_create_master_secret(PROVER_SECRET_ID)
    except AnoncredsMasterSecretDuplicateNameError:
        pass

    async def connection_routine(invitation: Invitation):
        # Создадим новый приватный DID для соединения с Inviter-ом
        my_did, my_verkey = await sirius_sdk.DID.create_and_store_my_did()
        me = sirius_sdk.Pairwise.Me(did=my_did, verkey=my_verkey)
        # Создадим экземпляр автомата для установки соединения на стороне Invitee
        invitee_machine = Invitee(
            me=me,
            my_endpoint=[e for e in await sirius_sdk.endpoints() if e.routing_keys == []][0],
            logger=Logger()
        )

        # Запускаем процесс установки соединения
        ok, pairwise = await invitee_machine.create_connection(
            invitation=invitation,
            my_label='Invitee'
        )
        # Сохраняем соединение в Wallet
        await sirius_sdk.PairwiseList.ensure_exists(pairwise)

    async def listener_routine():
        listener = await sirius_sdk.subscribe()
        # Ждем сообщение от Invitee
        async for event in listener:
            print(event)
            if isinstance(event.message, sirius_sdk.aries_rfc.OfferCredentialMessage):
                offer: sirius_sdk.aries_rfc.OfferCredentialMessage = event.message
                print('Prover: received credential offer')
                await asyncio.sleep(3)
                issuer: sirius_sdk.Pairwise = await sirius_sdk.PairwiseList.load_for_verkey(event["sender_verkey"])
                feature_0036 = sirius_sdk.aries_rfc.Holder(issuer, logger=Logger())
                print('Prover: start to process offer...')
                dkms = await sirius_sdk.ledger("indicio_test_network")
                success, cred_id = await feature_0036.accept(offer=offer, master_secret_id=PROVER_SECRET_ID, ledger=dkms)
                if success:
                    print(f'Prover: credential with cred-id: {cred_id} successfully stored to Wallet')
                else:
                    print(f'Prover: credential was not stored due to some problems')
                    if feature_0036.problem_report:
                        print('Prover: problem report:')
                        print(json.dumps(feature_0036.problem_report, indent=2, sort_keys=True))
            elif isinstance(event.message, sirius_sdk.aries_rfc.RequestPresentationMessage):
                proof_request: sirius_sdk.aries_rfc.RequestPresentationMessage = event.message
                print('Prover: received proof request')
                self_attested = {}
                for referent_id, data in proof_request.proof_request.get('requested_attributes', {}).items():
                    if not data.get('restrictions', None):
                        attr_name = data["name"]
                        attr_value = await ainput("Enter " + attr_name + ":")
                        self_attested[attr_name] = attr_value

                print('Prover: start verify...')
                dkms = await sirius_sdk.ledger("indicio_test_network")

                verifier = await sirius_sdk.PairwiseList.load_for_verkey(event["sender_verkey"])

                feature_0037 = sirius_sdk.aries_rfc.Prover(
                    verifier=verifier,
                    ledger=dkms,
                    logger=Logger(),
                    self_attested_identity=self_attested
                )
                success = await feature_0037.prove(request=proof_request, master_secret_id=PROVER_SECRET_ID)
                if success:
                    print(f'Prover: credentials was successfully proved')
                else:
                    print(f'Prover: credential was not proved')
                    if feature_0037.problem_report:
                        print('Prover: problem report:')
                        print(json.dumps(feature_0036.problem_report, indent=2, sort_keys=True))

    await asyncio.wait(
        [
            asyncio.ensure_future(listener_routine())
        ]
    )

    while True:
        case = await ainput("1 - Accept invitation \n\r"
                            "exit - Exit \n\r"
                            "Enter your option\n\r: ")
        if case == '1':
            data = decode(Image.open("C:\\Users\\Mikhail\\Downloads\\qr.png"))
            str_data = data[0].data.decode('utf8')
            index = str_data.find("?c_i=")
            str_data = str_data[(index + 5):-1]
            inv_json = json.loads(base64.b64decode(str_data.encode('utf8') + b'=' * (-len(str_data) % 4)))
            invitation = Invitation(**inv_json)
            await connection_routine(invitation)
        elif case == 'exit':
            break
        else:
            pass


if __name__ == '__main__':
    sirius_sdk.init(**HOLDER['SDK'])

    asyncio.get_event_loop().run_until_complete(run())
