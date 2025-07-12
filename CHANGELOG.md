# Changelog

## [0.3.0](https://github.com/S1M0N38/balatrobot/compare/v0.2.0...v0.3.0) (2025-07-12)


### Features

* **api:** add comprehensive function call logging system ([38a3ff9](https://github.com/S1M0N38/balatrobot/commit/38a3ff91cb75ad89b4e418cf7d9b624cb682ef83))
* **api:** integrate logging system into main mod ([3c4a09f](https://github.com/S1M0N38/balatrobot/commit/3c4a09f8b780497a71f17691c9261f7ed56d9eb5))


### Bug Fixes

* **api:** add event queue threshold check to skip_or_select_blind ([91e4613](https://github.com/S1M0N38/balatrobot/commit/91e4613652f7a560b3d97e4c23cd72e80bb0e0e1))
* **api:** correct blind state key from Large to Big in comment ([f7e5c42](https://github.com/S1M0N38/balatrobot/commit/f7e5c425e9b182fd2ec03b9f0de1312488e54a59))
* **api:** remove misleading comment and fix typo in logging system ([859a50a](https://github.com/S1M0N38/balatrobot/commit/859a50a7532781c305a4a011779e359d3601bd4e))


### Documentation

* **api:** add TODO comment for additional shop actions ([34071a2](https://github.com/S1M0N38/balatrobot/commit/34071a26ecc1624c0beefab1ae5a3279a4610575))
* **dev:** update commit command scope and co-author docs ([c089ff5](https://github.com/S1M0N38/balatrobot/commit/c089ff580ef70e485c3a8599eba4d1f6c121b20e))
* **dev:** update test suite metrics in CLAUDE.md ([cc5b159](https://github.com/S1M0N38/balatrobot/commit/cc5b159c391dbfd2876bd2421cfb957eb98d4aad))

## [0.2.0](https://github.com/S1M0N38/balatrobot/compare/v0.1.0...v0.2.0) (2025-07-11)


### Features

* add blind_on_deck to game_state and ftm code ([79da57f](https://github.com/S1M0N38/balatrobot/commit/79da57fe056186b26b7733ef18b9e1e42d4d6b9a))
* add extensive logging to python code ([56c7c80](https://github.com/S1M0N38/balatrobot/commit/56c7c80d3419d9dd11fbd5cbea513a76015c92f0))
* **api:** add cashout API function ([e9d86b0](https://github.com/S1M0N38/balatrobot/commit/e9d86b0e244f100f2ec2e9753883ec26afc3f713))
* **api:** add shop action support with next_round functionality ([6bcab8a](https://github.com/S1M0N38/balatrobot/commit/6bcab8a783ba0ecb12764d7d45a990c3f7fa7dc9))
* **api:** game over and no discard left edge cases ([5ad134a](https://github.com/S1M0N38/balatrobot/commit/5ad134afea7ec1fd30d27450bac474a69aaaa552))
* **api:** handle winning a round in play_hand_or_discard ([975b0b7](https://github.com/S1M0N38/balatrobot/commit/975b0b7da89d15239da8e8d75d3f67b77c26c5c9))
* **api:** implement play_hand_or_discard action ([2c0ae92](https://github.com/S1M0N38/balatrobot/commit/2c0ae92bc3350e7a7d6c7b15404346c55b127d1b))
* **api:** improve logging for function calls ([8ba681e](https://github.com/S1M0N38/balatrobot/commit/8ba681e69de239bb58dba581749ab052bfdca628))
* **api:** validate state in the usage of API functions ([94a58b5](https://github.com/S1M0N38/balatrobot/commit/94a58b51aba4346fef0e835bb20b14547f94afb1))
* **dev:** add commit command with conventional commits spec ([95e4067](https://github.com/S1M0N38/balatrobot/commit/95e4067f9027bb14868ebd764180e65b8e82959a))
* **dev:** add test command and improve process detection ([344d1d3](https://github.com/S1M0N38/balatrobot/commit/344d1d3edb594708fcc9b785f3a5f391d25ed145))
* implement game speed up ([b46995f](https://github.com/S1M0N38/balatrobot/commit/b46995f1b9a695ba031e1795dd7458d9796a87fc))
* init lua code socket server ([85b5249](https://github.com/S1M0N38/balatrobot/commit/85b52494a6866ff894db512261881ff07b5d7b41))
* update mod entry point to new lua code ([5158a56](https://github.com/S1M0N38/balatrobot/commit/5158a56715d7d0ed83e277fe77487976e7f6edc5))


### Bug Fixes

* action params format ([5478ede](https://github.com/S1M0N38/balatrobot/commit/5478edeab759943767f0e39ad1fb795e4e0bcfc7))
* include ActionSchema in __init__.py exporting ([72b06ab](https://github.com/S1M0N38/balatrobot/commit/72b06ab56385bf8a14fedf2b75783d59712740f4))
* key for G.GAME.skips ([d99b4c9](https://github.com/S1M0N38/balatrobot/commit/d99b4c91bf831a353b9069e251af40d52f0fba2b))
* lua type for BalatrobotConfig ([2ae6055](https://github.com/S1M0N38/balatrobot/commit/2ae605529fb1a8a0d13a93fde8585761607730e5))
* reduce default mod dt to 4/60 ([21ea63b](https://github.com/S1M0N38/balatrobot/commit/21ea63b73931a94621f65deb646d3048d07801e2))


### Documentation

* add CLAUDE.md with development guidelines and commands ([be7898e](https://github.com/S1M0N38/balatrobot/commit/be7898e1a231d762773b3f26ed6f31edd39e0c98))
* **dev:** clarify commit command formatting guidelines ([12130f2](https://github.com/S1M0N38/balatrobot/commit/12130f24c1262c4e8625d2468ea5522e46d9d351))
* **dev:** improve code documentation and comments ([b06c259](https://github.com/S1M0N38/balatrobot/commit/b06c259912b17cf246509a251f2bb7c776798804))
* **dev:** refine commit command workflow instructions ([c3340e6](https://github.com/S1M0N38/balatrobot/commit/c3340e6b00f6b29fd68993f224ff40337e2181d6))
* **dev:** update commit command co-author handling ([b554b44](https://github.com/S1M0N38/balatrobot/commit/b554b442daf3b686bbc28cfb46eed47ef1581555))
* **dev:** update test suite metrics after shop API addition ([8c49a7d](https://github.com/S1M0N38/balatrobot/commit/8c49a7d9197dcb6042de550f3ddc489f092be440))
* remove redundant commands and refine existing ones ([a1e4d07](https://github.com/S1M0N38/balatrobot/commit/a1e4d070e9279f75681a45b836679093596c893c))
* renamed log file and provide suggestion for Timeout errors ([ce6aa6d](https://github.com/S1M0N38/balatrobot/commit/ce6aa6d67fabc146a75805173a5044f776fed70c))
* update CLAUDE.md with test prerequisites and workflow ([f7436e0](https://github.com/S1M0N38/balatrobot/commit/f7436e01175c9ad22aaf95a7c86e401ec1162886))

## 0.1.0 (2025-07-06)


### Features

* add balatrobot logo ([b95d1d1](https://github.com/S1M0N38/balatrobot/commit/b95d1d1e363b55a692afe7aa1028ffd239e1143c))
* add decks and stakes enumns ([d89942b](https://github.com/S1M0N38/balatrobot/commit/d89942bbb45664eea8139dac90b93c28da0ea1e8))
* port balatrobot to new smods format ([bb24993](https://github.com/S1M0N38/balatrobot/commit/bb249932f35c3096dba2294507400db62c3c20e8))
* remove botlogger and simplify lua code ([e3dcbd5](https://github.com/S1M0N38/balatrobot/commit/e3dcbd5397934126051b851b7b4004a93b3ed852))
* remove start/stop balatro methods ([76a431a](https://github.com/S1M0N38/balatrobot/commit/76a431a56506a22ffebb119fce9d76b1c7ce66c1))
* update Bot with types and new abc methods ([da47254](https://github.com/S1M0N38/balatrobot/commit/da4725484f96d79fb8683467a8d8f0e90afceec7))
* update example bot to the new Bot class ([a996b06](https://github.com/S1M0N38/balatrobot/commit/a996b068eaa40f2dc1ec25c29f55220eb75e6d9a))
* update MyFirstBot to use Decks and Stakes enums ([6c0db6f](https://github.com/S1M0N38/balatrobot/commit/6c0db6fbeca0799249ed59c7046cbe04effd66e3))


### Documentation

* add api-protocol page to the docs ([11a7971](https://github.com/S1M0N38/balatrobot/commit/11a79715dd1a8416d80a68f0acdb1cc44203d41b))
* add dev env setup to bot-development.md ([f8a5b49](https://github.com/S1M0N38/balatrobot/commit/f8a5b4910a84a4d8a927cabe5a835d6c01a91065))
* add docs generated by llm ([1f5ef80](https://github.com/S1M0N38/balatrobot/commit/1f5ef80927858ef8a226dd233a0f0216990bf9d9))
* add homepage to docs ([77df9d6](https://github.com/S1M0N38/balatrobot/commit/77df9d636a0e99dc6de19bb06ba8002398077318))
* add logo configuration to mkdocs theme ([7ba1413](https://github.com/S1M0N38/balatrobot/commit/7ba14135b54a5c77ed3c40d12edfef2ab2925ad8))
* enhance mkdocs config ([8a1714e](https://github.com/S1M0N38/balatrobot/commit/8a1714efe5a0ed2eeb3aa96ebde617cfd24a78cb))
* expand documentation with new references and best practices ([f4f6003](https://github.com/S1M0N38/balatrobot/commit/f4f6003cd4c0d7af1aa89b67ec44ae60fe228ca4))
* fix mkdocs palette configuration format ([0756cd3](https://github.com/S1M0N38/balatrobot/commit/0756cd333861ec2d1fab71471cb9807356a64d08))
* improve bot-development page ([987e7eb](https://github.com/S1M0N38/balatrobot/commit/987e7eb0bbff3a912ccce9da250a2aab77faab90))
* remove content from troubleshooting ([8f454b4](https://github.com/S1M0N38/balatrobot/commit/8f454b4715796df9f965edc9d7687de09f1776e7))
* remove emoji from docs ([b5acd72](https://github.com/S1M0N38/balatrobot/commit/b5acd722f2ec3fe8c07fc8e498ac3429b726234f))
* remove legacy content in the README ([42cbde3](https://github.com/S1M0N38/balatrobot/commit/42cbde3b3de9c251bced3a0f92c6a29be5ca248e))
* remove legacy pages from mkdocs.yml ([2947b32](https://github.com/S1M0N38/balatrobot/commit/2947b32d7647cb71c4a742fb4a026ee705e8f4f2))
* remove legacy pages from the docs ([53cb13b](https://github.com/S1M0N38/balatrobot/commit/53cb13ba2dd033f58d267b1175a423ffc07cbf28))
* remove table of contents from md files ([249ec7e](https://github.com/S1M0N38/balatrobot/commit/249ec7e99feeff0ba3bf5228017fcd088618ea4a))
* simplify docs and add mermaid diagrams ([5fca88c](https://github.com/S1M0N38/balatrobot/commit/5fca88c9efd22c964eda1c6bb8adc9854f661ef1))
* update docs themes ([6059519](https://github.com/S1M0N38/balatrobot/commit/6059519b30849341fda3be73f960f729b5acaeb7))
* update installation guide ([6afc3cd](https://github.com/S1M0N38/balatrobot/commit/6afc3cd4235d37ead4bf4c12a3c576a985942582))
* update README ([325dd20](https://github.com/S1M0N38/balatrobot/commit/325dd205ae6a35b37c869b8c238eecf3e072c3b1))
* update README.md with docs and contributors ([ba2c9da](https://github.com/S1M0N38/balatrobot/commit/ba2c9da6a956d65aa1eef8c53af86e1c33f9686f))
* update the path of the example bot ([023dbb0](https://github.com/S1M0N38/balatrobot/commit/023dbb0a4af28e7cdf170981e3ceb0a9f4ebd1f8))
* updpate bot-development docs page ([c687417](https://github.com/S1M0N38/balatrobot/commit/c6874176334b6e50edea30b2fc08bd2270563e38))
