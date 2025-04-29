+++
date = '2025-04-29 13:47:51'
title = 'Frontier Rest API'
weight = 10
+++

CCP have published a REST API giving access to a wide range of endpoints, in each case they have published a OpenAPI compliance specification:

- **Stillness** (Closed Alpha): `https://blockchain-gateway-stillness.live.tech.evefrontier.com/` ([Swagger](https://blockchain-gateway-stillness.live.tech.evefrontier.com/docs/doc.json))
- **Nova** (Builder Sandbox): `https://world-api-nova.live.tech.evefrontier.com/` ([Swagger(https://world-api-nova.live.tech.evefrontier.com/docs/doc.json)])

## Insomnia

[Insomnia](https://insomnia.rest) is a cross-platform REST client, it supports OpenAPI directly. I have refined the Request Collection slightly to organize and label the endpoints better:

> [!IMPORTANT]
> You will need to be using Insomnia 11 or higher, and you can import it from your Personal Workspace.

```yaml
type: collection.insomnia.rest/5.0
name: EVE Frontier API v0.1.12
meta:
  id: wrk_a7c329af12a74d3dbe686af57c9817dc
  created: 1745927767854
  modified: 1745927767854
collection:
  - name: /
    meta:
      id: fld_ad7a2b12e1924c5c8bf50df3beeae9e5
      created: 1745927868493
      modified: 1745927966123
      sortKey: -1745927874896
    children:
      - name: game
        meta:
          id: fld_b3bbd0a12da1442d8a9838092b4a0c56
          created: 1745927900865
          modified: 1745928154975
          sortKey: -1745927929353
        children:
          - url: "{{ _.base_url }}/solarsystems"
            name: get all the solar systems (deprecated)
            meta:
              id: req_753ed744b8f34c38802a5a030e01e09b
              created: 1745927785452
              modified: 1745928225688
              isPrivate: false
              description: list all the solar systems currently in the application
              sortKey: -1745928055673
            method: GET
            settings:
              renderRequestBody: true
              encodeUrl: true
              followRedirects: global
              cookies:
                send: true
                store: true
              rebuildPath: true
          - url: "{{ _.base_url }}/types"
            name: get all game types (deprecated)
            meta:
              id: req_16c302ce0dd848b393817dc149ceaed0
              created: 1745927785453
              modified: 1745928227064
              isPrivate: false
              description: list all the types used in the world
              sortKey: -1745928055623
            method: GET
            settings:
              renderRequestBody: true
              encodeUrl: true
              followRedirects: global
              cookies:
                send: true
                store: true
              rebuildPath: true
          - url: "{{ _.base_url }}/solarsystems/:id"
            name: get one solar system (deprecated)
            meta:
              id: req_e5d963a5d8f94e9081bfd485e8ab15cd
              created: 1745927785453
              modified: 1745928224786
              isPrivate: false
              description: list one of the solar systems currently in the application
              sortKey: -1745928055723
            method: GET
            settings:
              renderRequestBody: true
              encodeUrl: true
              followRedirects: global
              cookies:
                send: true
                store: true
              rebuildPath: true
          - url: "{{ _.base_url }}/types/{{ _.id }}"
            name: get a single type (deprecated)
            meta:
              id: req_9cb94301071b48d2bb8a5ddee72abf4c
              created: 1745927785454
              modified: 1745928223867
              isPrivate: false
              description: get info about a single game type
              sortKey: -1745928055823
            method: GET
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
          id: fld_09a54369ad034955ab3ecd3ff636f0c4
          created: 1745927917770
          modified: 1745927931797
          sortKey: -1745927917770
        children:
          - url: "{{ _.base_url }}/killmails"
            name: get all the kill mails reports (deprecated)
            meta:
              id: req_edb6bbb87dc04166a470d48a88355d85
              created: 1745927785447
              modified: 1745928210996
              isPrivate: false
              description: list all the kill mails reported by players
              sortKey: -1745928002702
            method: GET
            settings:
              renderRequestBody: true
              encodeUrl: true
              followRedirects: global
              cookies:
                send: true
                store: true
              rebuildPath: true
          - url: "{{ _.base_url }}/metatransaction"
            name: submit a meta transaction
            meta:
              id: req_8ec05743dc7042488e9b50bc6ee7fc70
              created: 1745927785448
              modified: 1745928201295
              isPrivate: false
              description: |-
                submit a meta transaction
                Only bringOnline, bringOffline and setEntityMetadata are allowed
              sortKey: -1745928002802
            method: POST
            settings:
              renderRequestBody: true
              encodeUrl: true
              followRedirects: global
              cookies:
                send: true
                store: true
              rebuildPath: true
          - url: "{{ _.base_url }}/smartassemblies"
            name: get all the smart assemblies (deprecated)
            meta:
              id: req_b85ec95576bf475e82d270339887647e
              created: 1745927785448
              modified: 1745928217251
              isPrivate: false
              description: list all the smart assemblies currently in the world
              sortKey: -1745928002602
            method: GET
            settings:
              renderRequestBody: true
              encodeUrl: true
              followRedirects: global
              cookies:
                send: true
                store: true
              rebuildPath: true
          - url: "{{ _.base_url }}/smartcharacters"
            name: get all the smart characters (deprecated)
            meta:
              id: req_1fb5c9e5bb2940e0baae7b0d72e37f30
              created: 1745927785451
              modified: 1745928200853
              isPrivate: false
              description: list all the smart characters currently in the world
              sortKey: -1745928002902
            method: GET
            settings:
              renderRequestBody: true
              encodeUrl: true
              followRedirects: global
              cookies:
                send: true
                store: true
              rebuildPath: true
          - url: "{{ _.base_url }}/smartassemblies/{{ _.id }}"
            name: get a single smart assembly (deprecated)
            meta:
              id: req_751b59cd8f22456bb568ca9ab0ad0248
              created: 1745927785451
              modified: 1745928199369
              isPrivate: false
              description: retrieve one smart assembly with the given id
              sortKey: -1745928003002
            method: GET
            settings:
              renderRequestBody: true
              encodeUrl: true
              followRedirects: global
              cookies:
                send: true
                store: true
              rebuildPath: true
          - url: "{{ _.base_url }}/smartcharacters/{{ _.address }}"
            name: get a single smart character (deprecated)
            meta:
              id: req_27be5dfdab6147909ae56b4c53bb58ac
              created: 1745927785452
              modified: 1745928196420
              isPrivate: false
              description: retrieve one smart character with the given address
              sortKey: -1745928003102
            method: GET
            settings:
              renderRequestBody: true
              encodeUrl: true
              followRedirects: global
              cookies:
                send: true
                store: true
              rebuildPath: true
      - name: meta
        meta:
          id: fld_9d0619057f5941b2954ed619ca45b7c8
          created: 1745927940936
          modified: 1745927940936
          sortKey: -1745927940936
        children:
          - url: "{{ _.base_url }}/abis/config"
            name: get ABI with some config
            meta:
              id: req_16eef143b2c8448db56191cb797dbbbe
              created: 1745927785445
              modified: 1745927974552
              isPrivate: false
              description: retrieve the world contracts ABIs with some config
              sortKey: -1745927948334
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
              id: req_5a2dd871cc484110b51867ac50fe7889
              created: 1745927785446
              modified: 1745927971902
              isPrivate: false
              description: Tells you if the World API is ok
              sortKey: -1745927948434
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
              id: req_b3bb50f018554ecd9f9f2b88b6b210b6
              created: 1745927785446
              modified: 1745927948583
              isPrivate: false
              description: retrieve all the config needed to connect to our services
              sortKey: -1745927948534
            method: GET
            settings:
              renderRequestBody: true
              encodeUrl: true
              followRedirects: global
              cookies:
                send: true
                store: true
              rebuildPath: true
  - name: v2
    meta:
      id: fld_ed6088457e3649f6b3f5a108723471cb
      created: 1745927874796
      modified: 1745927874796
      sortKey: -1745927874796
    children:
      - name: meta
        meta:
          id: fld_1aaff5c88b3640ccba060e921b857205
          created: 1745927785444
          modified: 1745927924649
          sortKey: -1745927887984
        children:
          - url: "{{ _.base_url }}/v2/pod/verify"
            name: verify a POD
            meta:
              id: req_2e4c6c2e391a4aadb42ed9a6bae190d1
              created: 1745927785454
              modified: 1745927785454
              isPrivate: false
              description: verify a Provable Object Datatype object
              sortKey: -1745927785454
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
          id: fld_4974209010fa47d5ad54c83cad69e788
          created: 1745927785444
          modified: 1745927921254
          sortKey: -1745927887884
        children:
          - url: "{{ _.base_url }}/v2/killmails"
            name: get all reported killmails
            meta:
              id: req_87f5c0b7515d484d9f88f0de62c67785
              created: 1745927785454
              modified: 1745927785454
              isPrivate: false
              description: >-
                Retrieve all killmails that have been saved to the chain

                Endpoint is paginated, use the `limit`/`offset` query param to paginate
              sortKey: -1745927785454
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
          - url: "{{ _.base_url }}/v2/smartassemblies/{{ _.id }}"
            name: get a single smart assembly
            meta:
              id: req_2ff6f6160e3448bd8113425425a87135
              created: 1745927785455
              modified: 1745927785455
              isPrivate: false
              description: >-
                Retrieve one Smart Assembly with the given id

                if the assembly is a gate then the `.gate{}` will be filled

                if the assembly is a storage unit then the `.storage{}` object will be filled
              sortKey: -1745927785455
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
          - url: "{{ _.base_url }}/v2/smartassemblies"
            name: get all the smart assemblies
            meta:
              id: req_4acde8b2a9dc4711aa93bfed65d96962
              created: 1745927785455
              modified: 1745927785455
              isPrivate: false
              description: >-
                list all the smart assemblies currently in the world

                Endpoint is paginated, use the `limit`/`offset` query param to paginate
              sortKey: -1745927785455
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
          - url: "{{ _.base_url }}/v2/smartcharacters"
            name: get all the smart characters
            meta:
              id: req_2b5780bddf3b41d7b82a33f28fa6f2b9
              created: 1745927785456
              modified: 1745927785456
              isPrivate: false
              description: >-
                list all the smart characters currently in the world

                Endpoint is paginated, use the `limit`/`offset` query param to paginate
              sortKey: -1745927785456
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
          - url: "{{ _.base_url }}/v2/smartcharacters/{{ _.address }}"
            name: get a single smart character
            meta:
              id: req_791d417ebeb04420ac2ac07da7316762
              created: 1745927785457
              modified: 1745927785457
              isPrivate: false
              description: retrieve one smart character with the given address
              sortKey: -1745927785457
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
          id: fld_2ca0d6e145384a48ac9fd1e0469e0203
          created: 1745927785445
          modified: 1745927887828
          sortKey: -1745927887784
        children:
          - url: "{{ _.base_url }}/v2/smartcharacters/me/jumps"
            name: list all the jumps for the current user
            meta:
              id: req_3fa5cca52ea24231bab5355e57808217
              created: 1745927785456
              modified: 1745927785456
              isPrivate: false
              description: returns all the gate jumps that the current authenticated user made
              sortKey: -1745927785456
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
              id: req_4c25ec300ea44beebab1d542e9a31a6f
              created: 1745927785457
              modified: 1745927785457
              isPrivate: false
              description: returns a single jump by the given id that the current
                authenticated user made
              sortKey: -1745927785457
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
          - url: "{{ _.base_url }}/v2/solarsystems/{{ _.id }}"
            name: get one solar system
            meta:
              id: req_1fa21f4a8b4947cc8b6945c66b334de1
              created: 1745927785458
              modified: 1745927785458
              isPrivate: false
              description: get details about a single solar system
              sortKey: -1745927785458
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
          - url: "{{ _.base_url }}/v2/solarsystems"
            name: get all the solar systems
            meta:
              id: req_25e9d09b6cae4857b21b6248c3a26f2b
              created: 1745927785458
              modified: 1745927785458
              isPrivate: false
              description: >-
                list all the solar systems currently in the game

                Endpoint is paginated, use the `limit`/`offset` query param to paginate
              sortKey: -1745927785458
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
          - url: "{{ _.base_url }}/v2/types"
            name: get all the game types
            meta:
              id: req_f79f142449854b97888202e0ac3b3744
              created: 1745927785458
              modified: 1745927785458
              isPrivate: false
              description: >-
                list all the game types

                Endpoint is paginated, use the `limit`/`offset` query param to paginate
              sortKey: -1745927785458
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
          - url: "{{ _.base_url }}/v2/types/{{ _.id }}"
            name: get game type
            meta:
              id: req_ce570cebac38475ebc0fae43d5330278
              created: 1745927785459
              modified: 1745927880605
              isPrivate: false
              description: get details about a single game type
              sortKey: -1745927785559
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
cookieJar:
  name: Default Jar
  meta:
    id: jar_72e754a015f343588587489f06dc7651cc99bce4
    created: 1745927767856
    modified: 1745927767856
environments:
  name: Base Environment
  meta:
    id: env_72e754a015f343588587489f06dc7651cc99bce4
    created: 1745927767855
    modified: 1745927785442
    isPrivate: false
  data:
    base_url: "{{ _.scheme }}://{{ _.host }}{{ _.base_path }}"
  subEnvironments:
    - name: Nova
      meta:
        id: env_49b81e32732e46c69fb6d4f4c602b7cd
        created: 1745927785443
        modified: 1745927849921
        isPrivate: false
        sortKey: 1745927785443
      data:
        scheme: https
        host: world-api-nova.live.tech.evefrontier.com
      color: "#44ff00"
```