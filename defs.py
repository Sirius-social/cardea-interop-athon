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


# See all: https://github.com/thecardeaproject/cardea/tree/main/schemas
SCHEMA_IDS = [
    'RuuJwd3JMffNwZ43DcJKN1:2:Lab_Order:1.4',
    'RuuJwd3JMffNwZ43DcJKN1:2:Lab_Result:1.4',
    'RuuJwd3JMffNwZ43DcJKN1:2:Medical_Release:1.0',
    'RuuJwd3JMffNwZ43DcJKN1:2:Trusted_Traveler:1.4',
    'RuuJwd3JMffNwZ43DcJKN1:2:Vaccination:1.4',
    'RuuJwd3JMffNwZ43DcJKN1:2:Vaccine_Exemption:1.4'
]
