+++
date = '2025-06-11 17:04:29'
title = 'Frontier World API'
weight = 10
+++

CCP have published a REST API giving access to a wide range of endpoints, in each case they have published a OpenAPI compliance specification:

- **Stillness** (Closed Alpha): `https://blockchain-gateway-stillness.live.tech.evefrontier.com/` ([Swagger](https://blockchain-gateway-stillness.live.tech.evefrontier.com/docs/doc.json))
- **Nova** (Builder Sandbox): `https://world-api-nova.live.tech.evefrontier.com/` ([Swagger](https://world-api-nova.live.tech.evefrontier.com/docs/doc.json))


## Insomnia

[Insomnia](https://insomnia.rest) is a cross-platform REST client, it supports OpenAPI directly. I have refined the Request Collection slightly to organize and label the endpoints better:

You will need to be using Insomnia 11 or higher, you can import it into your personal workspace simply by having the YAML below in your clipboard before clicking **Import**; alternatively save the YAML to a file and import from your filesystem.

> [!TIP]
> If you want to access the authenticated endpoints you will need to add your JWT into the `api_key` into your Insomnia Environment, more information available in the [Migration Guide](/develop/migrating-v1-to-v2/#authentication)

```yaml
type: collection.insomnia.rest/5.0
name: EVE Frontier World API (v0.1.31)
meta:
  id: wrk_405cc18c44d84f4c82fb6f28dafe1d96
  created: 1749660438111
  modified: 1749660438111
collection:
  - name: meta
    meta:
      id: fld_fb5ba3fff2d54b2aa6182c001e7c1090
      created: 1749660554120
      modified: 1749660554120
      sortKey: -1749660554121
    children:
      - url: "{{ _.base_url }}/abis/config"
        name: get ABI with some config
        meta:
          id: req_567cf76e72fb4c0cb82702c89b0457c4
          created: 1749660554122
          modified: 1749660554122
          isPrivate: false
          description: retrieve the world contracts ABIs with some config
          sortKey: -1749660554122
        method: GET
        settings:
          renderRequestBody: true
          encodeUrl: true
          followRedirects: global
          cookies:
            send: true
            store: true
          rebuildPath: true
      - url: "{{ _.base_url }}/health"
        name: health endpoint
        meta:
          id: req_700d80d9b0c8485781526b102df3f9a3
          created: 1749660554123
          modified: 1749660554123
          isPrivate: false
          description: Tells you if the World API is ok
          sortKey: -1749660554123
        method: GET
        settings:
          renderRequestBody: true
          encodeUrl: true
          followRedirects: global
          cookies:
            send: true
            store: true
          rebuildPath: true
      - url: "{{ _.base_url }}/config"
        name: get config
        meta:
          id: req_cd75d56b136c4cd49cd52fc3d3ad59e4
          created: 1749660554123
          modified: 1749660554123
          isPrivate: false
          description: retrieve all the config needed to connect to our services
          sortKey: -1749660554123
        method: GET
        settings:
          renderRequestBody: true
          encodeUrl: true
          followRedirects: global
          cookies:
            send: true
            store: true
          rebuildPath: true
      - url: "{{ _.base_url }}/v2/pod/verify"
        name: verify a POD
        meta:
          id: req_b6e7bb8824ac484191003a8cf02d523b
          created: 1749660554126
          modified: 1749660554126
          isPrivate: false
          description: verify a Provable Object Datatype object
          sortKey: -1749660554126
        method: POST
        body:
          mimeType: application/json
          text: |-
            {
              "entries": {},
              "signature": "string",
              "signerPublicKey": "string"
            }
        headers:
          - name: Content-Type
            disabled: false
            value: application/json
        settings:
          renderRequestBody: true
          encodeUrl: true
          followRedirects: global
          cookies:
            send: true
            store: true
          rebuildPath: true
  - name: chain
    meta:
      id: fld_0d1ad38282cf423cb68dae1684e96e2b
      created: 1749660554121
      modified: 1749660554121
      sortKey: -1749660554121
    children:
      - url: "{{ _.base_url }}/metatransaction"
        name: submit a meta transaction
        meta:
          id: req_b8941874cbfe4f08b8d1ec0f6f7187ec
          created: 1749660554124
          modified: 1749660554124
          isPrivate: false
          description: |-
            submit a meta transaction
            Only bringOnline, bringOffline and setEntityMetadata are allowed
          sortKey: -1749660554124
        method: POST
        settings:
          renderRequestBody: true
          encodeUrl: true
          followRedirects: global
          cookies:
            send: true
            store: true
          rebuildPath: true
      - url: "{{ _.base_url }}/v2/killmails"
        name: get all reported killmails
        meta:
          id: req_3b320443881445f6be2a287e2369a3a2
          created: 1749660554125
          modified: 1749660554125
          isPrivate: false
          description: >-
            Retrieve all killmails that have been saved to the chain

            Endpoint is paginated, use the `limit`/`offset` query param to paginate
          sortKey: -1749660554125
        method: GET
        parameters:
          - name: limit
            disabled: true
            value: "10"
          - name: offset
            disabled: true
            value: "0"
        settings:
          renderRequestBody: true
          encodeUrl: true
          followRedirects: global
          cookies:
            send: true
            store: true
          rebuildPath: true
      - url: "{{ _.base_url }}/v2/smartassemblies"
        name: get all the smart assemblies
        meta:
          id: req_3e9c2043a86d41d69e7210d236adf61a
          created: 1749660554126
          modified: 1749660554126
          isPrivate: false
          description: >-
            list all the smart assemblies currently in the world

            Endpoint is paginated, use the `limit`/`offset` query param to paginate
          sortKey: -1749660554126
        method: GET
        parameters:
          - name: limit
            disabled: true
            value: "10"
          - name: offset
            disabled: true
            value: "0"
        settings:
          renderRequestBody: true
          encodeUrl: true
          followRedirects: global
          cookies:
            send: true
            store: true
          rebuildPath: true
      - url: "{{ _.base_url
          }}/v2/smartassemblies/75343970651982257052710820829442849942642924970\
          878978184835257992027850797979"
        name: get a single smart assembly
        meta:
          id: req_12268ca80a94441db66a77caa04ed38e
          created: 1749660554127
          modified: 1749661226755
          isPrivate: false
          description: >-
            Retrieve one Smart Assembly with the given id

            if the assembly is a gate then the `.gate{}` will be filled

            if the assembly is a storage unit then the `.storage{}` object will be filled
          sortKey: -1749660554127
        method: GET
        parameters:
          - name: format
            disabled: true
            value: string
        settings:
          renderRequestBody: true
          encodeUrl: true
          followRedirects: global
          cookies:
            send: true
            store: true
          rebuildPath: true
      - url: "{{ _.base_url }}/v2/smartcharacters"
        name: get all the smart characters
        meta:
          id: req_5f69707028f8459ba6b005f782440e23
          created: 1749660554128
          modified: 1749660554128
          isPrivate: false
          description: >-
            list all the smart characters currently in the world

            Endpoint is paginated, use the `limit`/`offset` query param to paginate
          sortKey: -1749660554128
        method: GET
        parameters:
          - name: limit
            disabled: true
            value: "10"
          - name: offset
            disabled: true
            value: "0"
        settings:
          renderRequestBody: true
          encodeUrl: true
          followRedirects: global
          cookies:
            send: true
            store: true
          rebuildPath: true
      - url: "{{ _.base_url
          }}/v2/smartcharacters/0x19957f367b81bd7711d316a451ade0d8fa8cb5bf"
        name: get a single smart character
        meta:
          id: req_69faafdd2e8b4f34bde1b84c2d20ee7e
          created: 1749660554131
          modified: 1749661210354
          isPrivate: false
          description: retrieve one smart character with the given address
          sortKey: -1749660554131
        method: GET
        parameters:
          - name: format
            disabled: true
            value: string
        settings:
          renderRequestBody: true
          encodeUrl: true
          followRedirects: global
          cookies:
            send: true
            store: true
          rebuildPath: true
  - name: game
    meta:
      id: fld_e3e8fcd20a4d40209442077f16d567b4
      created: 1749660554122
      modified: 1749661122070
      sortKey: -1749660554122
    children:
      - url: "{{ _.base_url }}/v2/fuels"
        name: available fuels for the smart assemblies
        meta:
          id: req_e23ae61bc54e41e39608cf0542fd041b
          created: 1749660554125
          modified: 1749660554125
          isPrivate: false
          sortKey: -1749660554125
        method: GET
        settings:
          renderRequestBody: true
          encodeUrl: true
          followRedirects: global
          cookies:
            send: true
            store: true
          rebuildPath: true
      - url: "{{ _.base_url }}/v2/smartcharacters/me/jumps"
        name: list all the jumps for the current user
        meta:
          id: req_39dc5680dca847eebf20e1be36074766
          created: 1749660554128
          modified: 1749661069197
          isPrivate: false
          description: returns all the gate jumps that the current authenticated user made
          sortKey: -1749660554128
        method: GET
        headers:
          - id: pair_f833bb2d2a134a5eaac5a813b9ae7f52
            disabled: false
        settings:
          renderRequestBody: true
          encodeUrl: true
          followRedirects: global
          cookies:
            send: true
            store: true
          rebuildPath: true
      - url: "{{ _.base_url }}/v2/smartcharacters/me/scans"
        name: list all the scans for the current user
        meta:
          id: req_62955bf9d38b4966b7baf70a1563c39b
          created: 1749660554129
          modified: 1749660554129
          isPrivate: false
          description: |-
            Returns all the scans that the current authenticated user saved
            Mocked data for now
          sortKey: -1749660554129
        method: GET
        headers:
          - name: Authorization
            disabled: false
            value: "{{ _.api_key }}"
        settings:
          renderRequestBody: true
          encodeUrl: true
          followRedirects: global
          cookies:
            send: true
            store: true
          rebuildPath: true
      - url: "{{ _.base_url }}/v2/smartcharacters/me/jumps/{{ _.id }}"
        name: get a single jump
        meta:
          id: req_ba721937423947f986dcc9151516ce0f
          created: 1749660554129
          modified: 1749660554129
          isPrivate: false
          description: returns a single jump by the given id that the current
            authenticated user made
          sortKey: -1749660554129
        method: GET
        parameters:
          - name: format
            disabled: true
            value: string
        headers:
          - name: Authorization
            disabled: false
            value: "{{ _.api_key }}"
        settings:
          renderRequestBody: true
          encodeUrl: true
          followRedirects: global
          cookies:
            send: true
            store: true
          rebuildPath: true
      - url: "{{ _.base_url }}/v2/smartcharacters/me/scans/{{ _.id }}"
        name: get a single scan
        meta:
          id: req_46c4e0a4ff614521bf8b06fb5b9676b3
          created: 1749660554130
          modified: 1749660554130
          isPrivate: false
          description: >-
            Returns a single scan by the given id that the current authenticated
            user saved

            Mocked data for now
          sortKey: -1749660554130
        method: GET
        parameters:
          - name: format
            disabled: true
            value: string
        headers:
          - name: Authorization
            disabled: false
            value: "{{ _.api_key }}"
        settings:
          renderRequestBody: true
          encodeUrl: true
          followRedirects: global
          cookies:
            send: true
            store: true
          rebuildPath: true
      - url: "{{ _.base_url }}/v2/solarsystems"
        name: get all the solar systems
        meta:
          id: req_9d5f5aae41be48e5900771cffb4fe4c3
          created: 1749660554131
          modified: 1749660554131
          isPrivate: false
          description: >-
            list all the solar systems currently in the game

            Endpoint is paginated, use the `limit`/`offset` query param to paginate
          sortKey: -1749660554131
        method: GET
        parameters:
          - name: limit
            disabled: true
            value: "10"
          - name: offset
            disabled: true
            value: "0"
        settings:
          renderRequestBody: true
          encodeUrl: true
          followRedirects: global
          cookies:
            send: true
            store: true
          rebuildPath: true
      - url: "{{ _.base_url }}/v2/solarsystems/30000001"
        name: get one solar system
        meta:
          id: req_63f1650bafa24e71b8c773b5bae9a9ac
          created: 1749660554132
          modified: 1749660888421
          isPrivate: false
          description: get details about a single solar system
          sortKey: -1749660554132
        method: GET
        parameters:
          - name: format
            disabled: true
            value: string
        settings:
          renderRequestBody: true
          encodeUrl: true
          followRedirects: global
          cookies:
            send: true
            store: true
          rebuildPath: true
      - url: "{{ _.base_url }}/v2/types/72244"
        name: get game type
        meta:
          id: req_73cc0a85425a4822b1e4d76d49dc4860
          created: 1749660554132
          modified: 1749660777413
          isPrivate: false
          description: get details about a single game type
          sortKey: -1749660554132
        method: GET
        parameters:
          - name: format
            disabled: true
            value: string
        settings:
          renderRequestBody: true
          encodeUrl: true
          followRedirects: global
          cookies:
            send: true
            store: true
          rebuildPath: true
      - url: "{{ _.base_url }}/v2/types"
        name: get all the game types
        meta:
          id: req_f9e10d0d8f5d4e3da80d839594e5102c
          created: 1749660554132
          modified: 1749660554132
          isPrivate: false
          description: >-
            list all the game types

            Endpoint is paginated, use the `limit`/`offset` query param to paginate
          sortKey: -1749660554132
        method: GET
        parameters:
          - name: limit
            disabled: true
            value: "100"
          - name: offset
            disabled: true
            value: "0"
        settings:
          renderRequestBody: true
          encodeUrl: true
          followRedirects: global
          cookies:
            send: true
            store: true
          rebuildPath: true
    authentication:
      type: bearer
      token: "{{ _.api_key }}"
cookieJar:
  name: Default Jar
  meta:
    id: jar_f83817b8e3e11b0a4fb6a7e3c6d5ff08d8163189
    created: 1749660438113
    modified: 1749660438113
environments:
  name: Base Environment
  meta:
    id: env_f83817b8e3e11b0a4fb6a7e3c6d5ff08d8163189
    created: 1749660438112
    modified: 1749660668363
    isPrivate: false
  data:
    scheme: https
    base_url: "{{ _.scheme }}://{{ _.host }}{{ _.base_path }}"
  subEnvironments:
    - name: Stillness
      meta:
        id: env_7f985d9a8e5643c9996756ab770c88dc
        created: 1749660554120
        modified: 1749661301468
        isPrivate: false
        sortKey: 1749660554120
      data:
        host: blockchain-gateway-stillness.live.tech.evefrontier.com
        api_key: eyABC.123
      color: "#ff4a00"
```