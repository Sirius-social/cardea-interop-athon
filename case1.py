import asyncio

import sirius_sdk
from defs import ISSUER, LAB_RESULT_SCHEMA_ID


HOLDER = ISSUER


async def run():
    async with sirius_sdk.context(**HOLDER['SDK']):

        endpoints_ = await sirius_sdk.endpoints()
        my_endpoint = [e for e in endpoints_ if e.routing_keys == []][0]

        # 1. Lab Enterprise Agent displays an invitation
        inv_url = input('Paste Lab invitation URL: ')
        invitation = sirius_sdk.aries_rfc.Invitation.from_url(inv_url)

        # 2. Holder Agent connects using the invitation
        my_did, my_verkey = await sirius_sdk.DID.create_and_store_my_did()
        me = sirius_sdk.Pairwise.Me(did=my_did, verkey=my_verkey)

        machine = sirius_sdk.aries_rfc.Invitee(me, my_endpoint, logger=logger)
        ok, pairwise = await machine.create_connection(invitation=invitation, my_label='We are champions')
        assert ok
        await sirius_sdk.PairwiseList.ensure_exists(pairwise)

        # 3. Lab Enterprise Agent requests identity information using the present-proof v. 1 protocol
        listener = await sirius_sdk.subscribe()
        async for event in listener:
            if isinstance(event.message, sirius_sdk.aries_rfc.RequestPresentationMessage):
                pass






if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(run())
