import sirius_sdk


ISSUER = {
    'SDK': {
        'server_uri': 'https://demo.socialsirius.com',
        'credentials': b'hMPfx0D1ptQa2fK8UPw7p9/Zf/UUEY9Ppk9oU92VO8IUHnc6oP5ov7f9PQ1NLIO5EHcqghOJvRoV7taA/vCd2+gRlardPTGGN2IQ2eifQIUF635ie4lgPZGiJSjWYcXm',
        'p2p': sirius_sdk.P2PConnection(
                my_keys=('6AxpcFTPihyWtjWQ35ehnnpJqcP1mmkFecGPgApo28G5', '33WzfeKMVjcCpNSJEUoXbdSZo174xk1U2aG9ZAwTsWsomw2Dr7MJTkXRxU6CPStr2PJoTdpRtseFCkKo29aDD4BX'),
                their_verkey='LQuue52xRKEYcZmQ84fzz2dGyXuv5LbyM12pejUg9Hy'
            )
    },
    'DID': 'NazPugMFPWr4dTU8cSMtcd',
    'VERKEY': 'CmNrnhsQrsGSEaVX8MQ34RYQwekcrBWHQeUSZxCYQNBT'
}

LAB_AGENT_CREDS = ISSUER
LAB_DID = LAB_AGENT_CREDS["DID"]


VERIFIER = {
    'SDK': {
        'server_uri': 'https://demo.socialsirius.com',
        'credentials': b'hMPfx0D1ptQa2fK8UPw7p9/Zf/UUEY9Ppk9oU92VO8IUHnc6oP5ov7f9PQ1NLIO5EHcqghOJvRoV7taA/vCd27dfNDKGk1lHqBCjpgHwwotACFHXe3JwIxBUoVBFOMW0',
        'p2p': sirius_sdk.P2PConnection(
                my_keys=('4MnPFkkZ3NWZ2vRq5U3mQhZPkGw6y1DQCzynd4kyYtUw', '24gsMTc77ZHoGFCbQrTEEgTGFSZkK6WhUZKJySC19QswJ1mPZKSZnH9ohzn686UYBD9fj5TCAzxUiwzYhamk64Hu'),
                their_verkey='31qXP2rhZPMXvZTm1PrdvBNrmSdxxTNxVNgmKMAuPKJ3'
            )
    },
    'DID': 'Jj9FsbrRkcrPrB4PFZFRg7',
    'VERKEY': 'AfNcBeyuPZ5WKbiNQKw9vogzkYQggU8BsaTyAaMDfkQv'
}

HOLDER = {
    'SDK': {
        'server_uri': 'https://demo.socialsirius.com',
        'credentials': b'hMPfx0D1ptQa2fK8UPw7p9/Zf/UUEY9Ppk9oU92VO8IUHnc6oP5ov7f9PQ1NLIO5EHcqghOJvRoV7taA/vCd26wDD3pMSPKP490GjCvjlkmOC5pRJ47qJo+Xx/mi743t',
        'p2p': sirius_sdk.P2PConnection(
            my_keys=('5c7VPHiRXpEarAS3bwExURRQpNet2YqTboBjfT77GSUt', '23YcJp98mdKqM86Zh9q8hQN2JqrjaonfXGNJeuvtzsbyunKo4KosNpQFScYoceGhTjymxSwjDnxMmBGho834drTv'),
            their_verkey='5YtTtPa6Q1x2Xy7EMhJts3xqVNZtudjRDoqZD2Mhg8yN'
        )
    },
    # Does not make sense for Holder
    'DID': 'UXE2pJUCC3mDgU5UBKyLXX',
    'VERKEY': 'FzzouvZ4MqENPXxGwue3S1zguucpD47FbedpUxb31qwS'
}


LAB = {
    'SDK': {
        'server_uri': 'https://demo.socialsirius.com',
        'credentials': b'hMPfx0D1ptQa2fK8UPw7p9/Zf/UUEY9Ppk9oU92VO8IUHnc6oP5ov7f9PQ1NLIO5EHcqghOJvRoV7taA/vCd28f9cZJym6VMb+wus3RwPeyV1ze+MeCZhLZ+KRJzmdZR',
        'p2p': sirius_sdk.P2PConnection(
            my_keys=('5rzyEdyTkLyeJmMC9VUvEPx4hozkHkB47cXHwmS4T3Cu', '29Yj3tp2ewETQknzt1eZFkt1vn9riA8Abos1VA7E3KAgx1UbsBVknTVvSKrioQsnoJEUV5heqLNuqghHnYcjQuUM'),
            their_verkey='5MwrFLPP91phaEe5QjDAUhj4kmqQHkZszbNksFxqXWSM'
        )
    },
    'DID': '9UVPoNm8fqhWUsnm6mcuGd',
    'VERKEY': '5csxHQdoAyhi5VUeLsv97dtGnueeRRpHpE6XRuF8xGVP'
}


GOV = {
    'SDK': {
        'server_uri': 'https://demo.socialsirius.com',
        'credentials': b'hMPfx0D1ptQa2fK8UPw7p9/Zf/UUEY9Ppk9oU92VO8IUHnc6oP5ov7f9PQ1NLIO5EHcqghOJvRoV7taA/vCd29jfRMZ9/VdiFHKHxS3FdtMT19uY7Os7ERst14ASRcf5',
        'p2p': sirius_sdk.P2PConnection(
            my_keys=('3r8TRFsAZZNjmxFb8Hb5XVuJm7rdttyVcqbhLb6z1ay9', '2z4ED7MskwBrrSgzdcHSzusrqhDajUidrrGXXHrNvzfGoxvDDbM6pXUzKXVB6TSdoaVQUN8sgBn7UbrnfA15dKVD'),
            their_verkey='3x82GoLgC3WZ2nnjYZaqwFnbtaq9kxXEMRf2QHq1bF5G'
        )
    },
    'DID': 'UZ6ULjvZj4Pog7SDrKxXGx',
    'VERKEY': 'G21uvChANhXCxXVe7F9VQeAc6eyt7fZ1hYHHRR3YVNry'
}


GOV_AGENT_CREDS = VERIFIER
GOV_DID = GOV_AGENT_CREDS['DID']
VERIFIER_AGENT_CREDS = VERIFIER


# See all: https://github.com/thecardeaproject/cardea/tree/main/schemas
SCHEMA_IDS = [
    'RuuJwd3JMffNwZ43DcJKN1:2:Lab_Order:1.4',
    'RuuJwd3JMffNwZ43DcJKN1:2:Lab_Result:1.4',
    'RuuJwd3JMffNwZ43DcJKN1:2:Medical_Release:1.0',
    'RuuJwd3JMffNwZ43DcJKN1:2:Trusted_Traveler:1.4',
    'RuuJwd3JMffNwZ43DcJKN1:2:Vaccination:1.4',
    'RuuJwd3JMffNwZ43DcJKN1:2:Vaccine_Exemption:1.4'
]

LAB_RESULT_SCHEMA_ID = 'RuuJwd3JMffNwZ43DcJKN1:2:Lab_Result:1.4'
LAB_VACCINATION_SCHEMA_ID = 'RuuJwd3JMffNwZ43DcJKN1:2:Vaccination:1.4'
TRUSTED_TRAVELER_SCHEMA_ID = 'RuuJwd3JMffNwZ43DcJKN1:2:Trusted_Traveler:1.4'
