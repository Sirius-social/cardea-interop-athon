import json
import asyncio
from datetime import datetime

import sirius_sdk
from sirius_sdk.errors.indy_exceptions import AnoncredsMasterSecretDuplicateNameError


SDK = {
    'server_uri': 'https://demo.socialsirius.com',
    'credentials': b'hMPfx0D1ptQa2fK8UPw7p9/Zf/UUEY9Ppk9oU92VO8IUHnc6oP5ov7f9PQ1NLIO5EHcqghOJvRoV7taA/vCd203IiNQ2s5t8ftBtPVK1PuDY9J//qs2yyMWzx+GC30+5HYa49735BoHgi+U8ol+61w==',
    'p2p': sirius_sdk.P2PConnection(
            my_keys=('59Z7dCofBtrqQy7VxwUdQVGvgFKuDQUL7v4k9R2Hf9po', '32a3D7zovL6YY1pZ5xdYTLSd7qzjvuN3hHUnpFrYYFeazUeEfkeCnrhthSj6mg4RL7oM6gmHTVMBNM3RodvvbRe3'),
            their_verkey='26GJnrgS8oNc39i9ActwVd6ecWnvDjXCMv978j7j7aRt'
        )
}


async def logger(**kwargs):
    print('----------- LOGGER --------------')
    print(json.dumps(kwargs, indent=2, sort_keys=True))
    print('---------------------------------')


async def run_agent():
    async with sirius_sdk.context(**SDK):
        connection_key = await sirius_sdk.Crypto.create_key()
        endpoints = await sirius_sdk.endpoints()
        endpoint = [e for e in endpoints if e.routing_keys == []][0]
        dkms = await sirius_sdk.ledger('indicio_test_network')
        master_secret_id = 'secret_id'
        try:
            await sirius_sdk.AnonCreds.prover_create_master_secret(master_secret_id)
        except AnoncredsMasterSecretDuplicateNameError:
            pass

        print('***********************************************')
        print(f'CONNECTION_KEY: {connection_key}')
        print('***********************************************')
        my_invitation = sirius_sdk.aries_rfc.Invitation(
            label='Sirius-Issuer-' + str(datetime.utcnow()),
            recipient_keys=[connection_key],
            endpoint=endpoint.address,
        )
        my_invitation_url = 'http://socialsirius.com' + my_invitation.invitation_url
        print('Invitation URL: ' + my_invitation_url)
        qr_url = await sirius_sdk.generate_qr_code(my_invitation_url)
        print('Scan this QR in mobile App: ' + qr_url)
        listener = await sirius_sdk.subscribe()
        print('!!!!!!!! Run Agent loop !!!!!!!!!!!')
        async for event in listener:
            if isinstance(event.message, sirius_sdk.aries_rfc.ConnRequest):
                print('========== RUN 0160 =============')
                request: sirius_sdk.aries_rfc.ConnRequest = event.message
                my_did, my_verkey = await sirius_sdk.DID.create_and_store_my_did()
                rfc_0160 = sirius_sdk.aries_rfc.Inviter(
                    me=sirius_sdk.Pairwise.Me(my_did, my_verkey),
                    connection_key=connection_key,
                    my_endpoint=endpoint,
                    logger=logger
                )
                success, p2p = await rfc_0160.create_connection(request)
                assert success
                print('========== PAIRWISE ==============')
                print(json.dumps(p2p.metadata, indent=2, sort_keys=True))
                await sirius_sdk.PairwiseList.ensure_exists(p2p)
                print('==================================')
            else:
                print('========== Non processed message =============')
                print(json.dumps(dict(event.message), indent=2, sort_keys=True))
                print('==================================')


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(run_agent())
