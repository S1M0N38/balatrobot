# Changelog

## [0.6.1](https://github.com/coder/balatrobot/compare/v0.6.0...v0.6.1) (2025-10-23)


### Bug Fixes

* increase timeout for balatrobot client to 60 seconds ([edf26e2](https://github.com/coder/balatrobot/commit/edf26e29c845a12de65f1fab2ce117643000edd6))

## 0.6.0 (2025-10-22)


### Features

* add --status option to show running balatro instances ([bcfeb91](https://github.com/coder/balatrobot/commit/bcfeb911dcb35fecce1db64403ad55997e919b4c))
* add ante value to game state ([f7193c4](https://github.com/coder/balatrobot/commit/f7193c4385edf2afb94bb8c63b590358943b3acc))
* add audio flag to balatrobot (disabled by default) ([9c2db00](https://github.com/coder/balatrobot/commit/9c2db0079f50b7d37c93f473df11453b4db38bc3))
* add balatro enums ([fc8d6b4](https://github.com/coder/balatrobot/commit/fc8d6b45ce9d945351922cd312d5371f79c5b572))
* add balatro.sh script for running multiple instances ([d66fe98](https://github.com/coder/balatrobot/commit/d66fe9856d05a1540c1c672e827ecbdc9b36baac))
* add balatrobot logo ([b95d1d1](https://github.com/coder/balatrobot/commit/b95d1d1e363b55a692afe7aa1028ffd239e1143c))
* add blind_on_deck to game_state and ftm code ([79da57f](https://github.com/coder/balatrobot/commit/79da57fe056186b26b7733ef18b9e1e42d4d6b9a))
* add card limit to joker game data ([8cb99cf](https://github.com/coder/balatrobot/commit/8cb99cf1167036878733b28b4d067d5d55ce0c75))
* add cards argument to use_consumable ([1775952](https://github.com/coder/balatrobot/commit/17759523b97c1b5de91c0542b79282894265c49a))
* add check and test case for whether a buy_and_use_card target can be used ([dab8f19](https://github.com/coder/balatrobot/commit/dab8f19e7953c47f879eaf5ca6196f0aa2325788))
* add decks and stakes enumns ([d89942b](https://github.com/coder/balatrobot/commit/d89942bbb45664eea8139dac90b93c28da0ea1e8))
* add extensive logging to python code ([56c7c80](https://github.com/coder/balatrobot/commit/56c7c80d3419d9dd11fbd5cbea513a76015c92f0))
* add hook for buy_card, should work with buy_and_use card ([a6b8b0f](https://github.com/coder/balatrobot/commit/a6b8b0f530690dff21ae51e143c6c85ffaacf161))
* add hook for joker rearrangement ([c9fe966](https://github.com/coder/balatrobot/commit/c9fe966ae23ee0fe76b70f234447ad270d4c457d))
* add hook for sell_consumable ([e390761](https://github.com/coder/balatrobot/commit/e3907615ae96f553be96699285d598f868c179ee))
* add hook for use_consumable ([d54042c](https://github.com/coder/balatrobot/commit/d54042c4a7d5e403aab7a920b5ded6e73a8074d2))
* add rearrange consumeables endpoint ([404de7d](https://github.com/coder/balatrobot/commit/404de7df85156322caa7add619700b63d5197a5e))
* add rearrange jokers endpoint ([b63c500](https://github.com/coder/balatrobot/commit/b63c500d5c91dd6cfcb55d9cb0aa396fa0f4115e))
* add RearrangeConsumeablesArgs type ([e7796cc](https://github.com/coder/balatrobot/commit/e7796cc6a13f32806a02438afdebc474dbe7c9a7))
* add redeem_voucher ([70e8cb0](https://github.com/coder/balatrobot/commit/70e8cb0bf4ab9788e03cccea51031cfa5e23e735))
* add render on api env var / flag ([b96e623](https://github.com/coder/balatrobot/commit/b96e623bcb8962bbb513ebeddacedbdb05c13c23))
* add reroll cost &lt; dollars check ([644f667](https://github.com/coder/balatrobot/commit/644f6674bf2247189dd7bc4df5a79667426fbb40))
* add reroll shop action ([1202866](https://github.com/coder/balatrobot/commit/12028661c86c9e441297dc0728e0acf0fcb33f63))
* add sell consumable completion condition ([dcff055](https://github.com/coder/balatrobot/commit/dcff0552734718016b7ce7fe95cd6b09aa3dbe36))
* add sell consumable endpoint ([c467611](https://github.com/coder/balatrobot/commit/c467611abc0d40f1b2b88390b3bd2b8fe2bc2978))
* add sell joker completion condition ([e4b3b6e](https://github.com/coder/balatrobot/commit/e4b3b6eb9111d0e2e96b278b818745523cc2ee42))
* add sell joker endpoint ([183db62](https://github.com/coder/balatrobot/commit/183db629bcb053ba4db5f7a8e510c90a2d95d6a1))
* add sell joker types ([876a249](https://github.com/coder/balatrobot/commit/876a249c58f1e7399c231d1d424876ae2c994cd7))
* add sell_joker hook for logging ([44df912](https://github.com/coder/balatrobot/commit/44df9123bc95fffbbdf0e95fe496e5e3825a83f3))
* add settings.lua for configuring Balatro ([4b36304](https://github.com/coder/balatrobot/commit/4b363046db6cdf9a6383a04048546889f0b203ae))
* add shop_idle() cond for actions that do not depart the shop ([987e965](https://github.com/coder/balatrobot/commit/987e96564548ba64482fe2b2e2aec395696a4b24))
* add sort_id to card in game state ([77bc507](https://github.com/coder/balatrobot/commit/77bc5078e7cbcff2ca219ac57f534734315cce27))
* add state checking for use consumable with cards parameter ([ec123d6](https://github.com/coder/balatrobot/commit/ec123d6706e9681382e88df68a3b2a9dcf6961aa))
* add test-migrate target to Makefile ([5c41d17](https://github.com/coder/balatrobot/commit/5c41d170dda7afb9c61e7c1d65a5692b0fcbf180))
* add types for joker card limit and count ([207c41b](https://github.com/coder/balatrobot/commit/207c41b15a655dd9c125ae4a375d57ce2ded85a9))
* add types for sell consumable ([b395430](https://github.com/coder/balatrobot/commit/b3954303b31b3276d6a4452404a9e9034f6bd8e1))
* add use consumable endpoint ([012a957](https://github.com/coder/balatrobot/commit/012a95777f7424e211fd02cae74bc84a4766d7e5))
* add use_consumable completion condition ([44cdcf7](https://github.com/coder/balatrobot/commit/44cdcf714b28eb17495b8df56856dfb826231885))
* added tests and gamestate for reroll shop ([4bc1b61](https://github.com/coder/balatrobot/commit/4bc1b619c5dcec02815a46c338f9c57917b7dd41))
* **api:** add cashout API function ([e9d86b0](https://github.com/coder/balatrobot/commit/e9d86b0e244f100f2ec2e9753883ec26afc3f713))
* **api:** add comprehensive error handling and validation system ([c00eca4](https://github.com/coder/balatrobot/commit/c00eca477caee4a2b3a816db4884e425eb85cded))
* **api:** add comprehensive function call logging system ([38a3ff9](https://github.com/coder/balatrobot/commit/38a3ff91cb75ad89b4e418cf7d9b624cb682ef83))
* **api:** add hands_left to current_round game state ([79cec38](https://github.com/coder/balatrobot/commit/79cec3832a679215fea5d77f83507ce2e611a643))
* **api:** add log_path optional param to start_run ([e9b986c](https://github.com/coder/balatrobot/commit/e9b986cc5c53f4692a2f3e7f1efa2d8d120d908c))
* **api:** add screenshot API endpoint ([165b58c](https://github.com/coder/balatrobot/commit/165b58c92426f5796c4d6327b175cc3c3ee818f4))
* **api:** add shop action support with next_round functionality ([6bcab8a](https://github.com/coder/balatrobot/commit/6bcab8a783ba0ecb12764d7d45a990c3f7fa7dc9))
* **api:** add shop booster field to game state ([48c4fd6](https://github.com/coder/balatrobot/commit/48c4fd6c0ea026b082c65f7bb84befa19a9a5fec))
* **api:** add shop jokers field to game state ([ad062bb](https://github.com/coder/balatrobot/commit/ad062bb5635839227882150735bfb92206ac4127))
* **api:** add shop vouchers field to game state ([b998062](https://github.com/coder/balatrobot/commit/b998062f4fcbcbe8e6bf1fc8c9abe81713e8cf2c))
* **api:** game over and no discard left edge cases ([5ad134a](https://github.com/coder/balatrobot/commit/5ad134afea7ec1fd30d27450bac474a69aaaa552))
* **api:** handle winning a round in play_hand_or_discard ([975b0b7](https://github.com/coder/balatrobot/commit/975b0b7da89d15239da8e8d75d3f67b77c26c5c9))
* **api:** implement play_hand_or_discard action ([2c0ae92](https://github.com/coder/balatrobot/commit/2c0ae92bc3350e7a7d6c7b15404346c55b127d1b))
* **api:** improve cards selection ranges in use consumeables ([b9ce462](https://github.com/coder/balatrobot/commit/b9ce46231030d6c58e082bcb9aa58f50b8506a4c))
* **api:** improve logging for function calls ([8ba681e](https://github.com/coder/balatrobot/commit/8ba681e69de239bb58dba581749ab052bfdca628))
* **api:** integrate logging system into main mod ([3c4a09f](https://github.com/coder/balatrobot/commit/3c4a09f8b780497a71f17691c9261f7ed56d9eb5))
* **api:** new improved game state object ([4e2f5ac](https://github.com/coder/balatrobot/commit/4e2f5ac3b28b982f77f90724ef122989e36941cb))
* **api:** new types for the G game state object ([7a23f6f](https://github.com/coder/balatrobot/commit/7a23f6f0a40c1bb2f1617c5892d112c2d70509ff))
* **api:** validate state in the usage of API functions ([94a58b5](https://github.com/coder/balatrobot/commit/94a58b51aba4346fef0e835bb20b14547f94afb1))
* better api errors ([617cbc9](https://github.com/coder/balatrobot/commit/617cbc9aaa40cf1b89aa8cf58ca0304af7dba7bf))
* **bot:** add standardized error codes enum ([2c9fdaa](https://github.com/coder/balatrobot/commit/2c9fdaaf1e0cfbfbb5586e633c0fa8cd97db496d))
* **bot:** add TCP-based replay bot for JSONL files ([b5b6cf8](https://github.com/coder/balatrobot/commit/b5b6cf8869c374c38b036353e5a81f8ded1a3b69))
* **bot:** replace Bot ABC with structured API client ([3a70fde](https://github.com/coder/balatrobot/commit/3a70fdef70a5647732155bc2608d37f5fdc10182))
* **bots:** improve replay script with proper CLI ([e38cbd4](https://github.com/coder/balatrobot/commit/e38cbd45681a8ce4eb6b1c9029683bd17b861709))
* checkpoints work ([1e78386](https://github.com/coder/balatrobot/commit/1e78386eea0a36c59339109bb6c92f48b4300016))
* **client:** add port option to client ([4c7b912](https://github.com/coder/balatrobot/commit/4c7b9123be535e2ddd62a25d857d75fd535d5cc9))
* **client:** add screenshot method ([0ee8b8c](https://github.com/coder/balatrobot/commit/0ee8b8ce54f163cfe8846263de520c0f75ae5764))
* created savefile-based checkpointing ([73ab99f](https://github.com/coder/balatrobot/commit/73ab99f2973370ac37b2b70fce5066c0fd64751d))
* **dev:** add commit command with conventional commits spec ([95e4067](https://github.com/coder/balatrobot/commit/95e4067f9027bb14868ebd764180e65b8e82959a))
* **dev:** add Makefile ([02c569f](https://github.com/coder/balatrobot/commit/02c569f1622be81558b160b9405387eca86b7913))
* **dev:** add test command and improve process detection ([344d1d3](https://github.com/coder/balatrobot/commit/344d1d3edb594708fcc9b785f3a5f391d25ed145))
* docs and types for checkpointing ([5efff03](https://github.com/coder/balatrobot/commit/5efff03d7741be192cc5154d3218f1b3619379b1))
* enhance rearrange jokers field in game state ([e72c78e](https://github.com/coder/balatrobot/commit/e72c78e868e7c65fbde925fb3b6dc9a252a4246f))
* **examples:** update example bot to use new client API ([73bf5b7](https://github.com/coder/balatrobot/commit/73bf5b7c19e15a65968de5c273b51754ffba2419))
* finish buy_and_use_card docs ([c644bab](https://github.com/coder/balatrobot/commit/c644bab9485649939e4714d247e0244c41d63047))
* hook reroll_shop ([0e533ae](https://github.com/coder/balatrobot/commit/0e533ae75ce464435c73e7aa914f4ec689808ac8))
* implement game speed up ([b46995f](https://github.com/coder/balatrobot/commit/b46995f1b9a695ba031e1795dd7458d9796a87fc))
* improve CLI for replay bot ([077178c](https://github.com/coder/balatrobot/commit/077178cb9af4b06b7e62dfa54bd5194aeddbd0e2))
* improved graphics settings for screenshots ([86af829](https://github.com/coder/balatrobot/commit/86af82956b261c1d1c6742355e162c8fd4c64125))
* init lua code socket server ([85b5249](https://github.com/coder/balatrobot/commit/85b52494a6866ff894db512261881ff07b5d7b41))
* **log:** add hand rearrange logging (WIP) ([7ea6b37](https://github.com/coder/balatrobot/commit/7ea6b37a0d19223bc5c479a11d4aced407999549))
* **log:** add JSONLLogEntry model and flexible arguments field ([3e8307a](https://github.com/coder/balatrobot/commit/3e8307a22277470b0627b1129149303b9f672ce5))
* **log:** add log module functions to Log type ([732039c](https://github.com/coder/balatrobot/commit/732039c499db7af69df9966bac040fd8d0f7b495))
* **log:** add logging to BalatroClient connection and API calls ([3776c9c](https://github.com/coder/balatrobot/commit/3776c9c58eae1971393b8e738f6454e87ee2ba83))
* **log:** add types for log module ([719e3ff](https://github.com/coder/balatrobot/commit/719e3ff64130c93376ae6d60602f92509e09a137))
* **log:** hook for rearrange_consumeables ([06f5be7](https://github.com/coder/balatrobot/commit/06f5be75ba1a75fef766ea05a858e4e19f788e9c))
* **log:** improved logging system ([#39](https://github.com/coder/balatrobot/issues/39)) ([919f59d](https://github.com/coder/balatrobot/commit/919f59d9406e36137fa95c85674e2e162dae94aa))
* **log:** ts before and after for each log entry and refactoring ([40fd9ba](https://github.com/coder/balatrobot/commit/40fd9ba5f824bb6e41911bcf55373b3cb67a100b))
* make host configurable via env var ([0fc9b9b](https://github.com/coder/balatrobot/commit/0fc9b9b476f93bb65cdf1669d735bb5fbb3d099f))
* markdown format ([f361c9c](https://github.com/coder/balatrobot/commit/f361c9c308002fb3c48a6eac780da8bb6b7f405e))
* move checkpoint binaries to git lfs ([5b3c513](https://github.com/coder/balatrobot/commit/5b3c5134417841c500c0fab9006ba62fb63fce22))
* port balatrobot to new smods format ([bb24993](https://github.com/coder/balatrobot/commit/bb249932f35c3096dba2294507400db62c3c20e8))
* prototyping checkpoint system ([7bdf5e2](https://github.com/coder/balatrobot/commit/7bdf5e26667e70d3f0c5e404b31f49c0b9f65a79))
* redeem voucher docs ([8e894e0](https://github.com/coder/balatrobot/commit/8e894e0d120e9b2d135c75e4d6345bd9038b39f4))
* remove botlogger and simplify lua code ([e3dcbd5](https://github.com/coder/balatrobot/commit/e3dcbd5397934126051b851b7b4004a93b3ed852))
* remove start/stop balatro methods ([76a431a](https://github.com/coder/balatrobot/commit/76a431a56506a22ffebb119fce9d76b1c7ce66c1))
* reroll shop types ([40a9e33](https://github.com/coder/balatrobot/commit/40a9e337dc9698a7a25653b86d5893d7ce3c8ce5))
* reroll_shop docs ([845799c](https://github.com/coder/balatrobot/commit/845799c77ba662a87f61fa37ca3d52523addcbd7))
* revert bloom string ([b366f15](https://github.com/coder/balatrobot/commit/b366f15fff7ce8220962cf19ef2548ecf179a924))
* shop condition based on timing ([b713204](https://github.com/coder/balatrobot/commit/b713204bc6fd54a65642af5f43bf05b80f25f96d))
* skip initial splash screen when starting Balatro ([58922f2](https://github.com/coder/balatrobot/commit/58922f22fb1c7319af3e92072bb06b9b71d034f6))
* stylua ([8bbc51a](https://github.com/coder/balatrobot/commit/8bbc51a39b7309892d10051c9d86c5d65fa52ecf))
* tests for checkpointign ([9c04ff6](https://github.com/coder/balatrobot/commit/9c04ff6ae6e305e7f1fb65af9aaf0f0139bb2393))
* tests for redeem_voucher ([5982d82](https://github.com/coder/balatrobot/commit/5982d828e4509db2bc2797843374fb223beab1cb))
* **tests:** add TCP client support to test infrastructure ([ff935f3](https://github.com/coder/balatrobot/commit/ff935f3f39b873e97a580f02fe8204f2e03565d3))
* track test checkpoints with git lfs ([0ecbb43](https://github.com/coder/balatrobot/commit/0ecbb43f54a9e325403c19458efdbc7bc19c5b36))
* update Bot with types and new abc methods ([da47254](https://github.com/coder/balatrobot/commit/da4725484f96d79fb8683467a8d8f0e90afceec7))
* update example bot to the new Bot class ([a996b06](https://github.com/coder/balatrobot/commit/a996b068eaa40f2dc1ec25c29f55220eb75e6d9a))
* update game state with consumeables ([2fb2cbc](https://github.com/coder/balatrobot/commit/2fb2cbc1d46ea5b9a6cd08093f95df97e1aa768d))
* update mod entry point to new lua code ([5158a56](https://github.com/coder/balatrobot/commit/5158a56715d7d0ed83e277fe77487976e7f6edc5))
* update models to match lua types ([0a224ea](https://github.com/coder/balatrobot/commit/0a224ea43078eff4ca3a81e9ad26d44e7419a896))
* update MyFirstBot to use Decks and Stakes enums ([6c0db6f](https://github.com/coder/balatrobot/commit/6c0db6fbeca0799249ed59c7046cbe04effd66e3))
* updated types for redeem_voucher ([9fe3e67](https://github.com/coder/balatrobot/commit/9fe3e672965eb78686978bd6c0d3cb51099dc968))
* using checkpoints in test_shop ([4c52efc](https://github.com/coder/balatrobot/commit/4c52efc45ba3f1ed42cc802de6ca6530beb70910))
* **utils:** add completion conditions table in utils ([a36f9eb](https://github.com/coder/balatrobot/commit/a36f9eb9ad2ca132b9ffd4116ab25df385016aa8))
* **utils:** add sets_equal function ([133b150](https://github.com/coder/balatrobot/commit/133b150a55e5dd068041202a13aec7929d5c877c))
* WIP save file manipulation ([8cbae31](https://github.com/coder/balatrobot/commit/8cbae31cd66bcb7e8864a1adeb337b0784cbd8b5))


### Bug Fixes

* action params format ([5478ede](https://github.com/coder/balatrobot/commit/5478edeab759943767f0e39ad1fb795e4e0bcfc7))
* add missing set fields in game state ([ee92ac0](https://github.com/coder/balatrobot/commit/ee92ac0a0596c1764e113693f8eff48138dd1f23))
* adjust balatro settings ([866d201](https://github.com/coder/balatrobot/commit/866d201e2d2d6ca5e3c2522072c9a4f415bae6d9))
* **api:** add card count validation to play_hand_or_discard function ([0072a0e](https://github.com/coder/balatrobot/commit/0072a0e8fbc078bde347f4bd5f1b771a911da4e8))
* **api:** add event queue threshold check to skip_or_select_blind ([91e4613](https://github.com/coder/balatrobot/commit/91e4613652f7a560b3d97e4c23cd72e80bb0e0e1))
* **api:** add event queue threshold check to start_run condition ([ea210ed](https://github.com/coder/balatrobot/commit/ea210ed47021f90106248bbf8cced3e9f9e7c878))
* **api:** add event queue threshold to skip_or_select_blind ([f9c6f04](https://github.com/coder/balatrobot/commit/f9c6f046a31ae6045f077a15c0e06f8225fc2d81))
* **api:** add seed warning for non-reproducible runs ([b996f45](https://github.com/coder/balatrobot/commit/b996f45ff41252fa91fdb341c1f1c96b93b73712))
* **api:** clear hand highlights before selecting new cards ([9efb351](https://github.com/coder/balatrobot/commit/9efb35181be306234c34a6f3f2da3c2308356c5e))
* **api:** correct blind state key from Large to Big in comment ([f7e5c42](https://github.com/coder/balatrobot/commit/f7e5c425e9b182fd2ec03b9f0de1312488e54a59))
* **api:** correct socket type references from UDP to TCP ([149d314](https://github.com/coder/balatrobot/commit/149d3148184561b86562dac2e4604ac117fbf0ec))
* **api:** prevent skipping Boss blind in skip_or_select_blind ([dc66e7e](https://github.com/coder/balatrobot/commit/dc66e7e75aeaaaf6cd9b32c30c424688a40ab548))
* **api:** remove misleading comment and fix typo in logging system ([859a50a](https://github.com/coder/balatrobot/commit/859a50a7532781c305a4a011779e359d3601bd4e))
* buy card hook ([#68](https://github.com/coder/balatrobot/issues/68)) ([6412506](https://github.com/coder/balatrobot/commit/64125065c1ff4c6fe1993a09d8ff4448a6b32f25))
* **ci:** correct YAML indentation in deploy docs workflow ([ca2d797](https://github.com/coder/balatrobot/commit/ca2d797b4c73dfb6cb869af995a0caaf2913bbad))
* **client:** increase timeout to 30s ([6f315e1](https://github.com/coder/balatrobot/commit/6f315e160f10f0870dc9f483843750d5714fd9eb))
* **client:** make arguments optional in send_message ([56419f5](https://github.com/coder/balatrobot/commit/56419f55c6a87e9fc74b5bc10ed6dfd1b4890bb2))
* **dev:** remove --check flag from mdformat command ([3f710b8](https://github.com/coder/balatrobot/commit/3f710b8ba13a79432284732ee420e778e45915ac))
* effect for c_eris ([fd564ce](https://github.com/coder/balatrobot/commit/fd564cec6e98cbff11d0bd7499773a87535ce676))
* fast profile for balatro ([ac4eaa5](https://github.com/coder/balatrobot/commit/ac4eaa5f3b27fd9442e400e96a712bcbed36ccfb)), closes [#83](https://github.com/coder/balatrobot/issues/83)
* include ActionSchema in __init__.py exporting ([72b06ab](https://github.com/coder/balatrobot/commit/72b06ab56385bf8a14fedf2b75783d59712740f4))
* key for G.GAME.skips ([d99b4c9](https://github.com/coder/balatrobot/commit/d99b4c91bf831a353b9069e251af40d52f0fba2b))
* **log:** update type definitions to match implementation ([4bbe051](https://github.com/coder/balatrobot/commit/4bbe051dd84a76d2bbe3fd76bda9cb2f30944b56))
* long messages limit in luasocket ([7d6168b](https://github.com/coder/balatrobot/commit/7d6168ba9895246580aed5c6587657388c4289a0))
* lua type for BalatrobotConfig ([2ae6055](https://github.com/coder/balatrobot/commit/2ae605529fb1a8a0d13a93fde8585761607730e5))
* make use of shutil.move instead of os.rename ([c908326](https://github.com/coder/balatrobot/commit/c908326adf45671ce4f7c368473a0da6a12b2813))
* reduce default mod dt to 4/60 ([21ea63b](https://github.com/coder/balatrobot/commit/21ea63b73931a94621f65deb646d3048d07801e2))
* remove set_ranks and align_cards from rearrange_hand ([7ae211e](https://github.com/coder/balatrobot/commit/7ae211e5a589a53fc0fad59fc8c8bcb8d17cdc91))
* remove unused out of place test ([163e4a8](https://github.com/coder/balatrobot/commit/163e4a8149a55b63f22da8193872f301a1147676))
* revert shop() -&gt; cash_out() ([a2555a4](https://github.com/coder/balatrobot/commit/a2555a420284dfffced4c47c22d562fc2ac50f8a))
* shop check ([c77c52b](https://github.com/coder/balatrobot/commit/c77c52ba84310595ac7c7106f873314ed9eb64a0))
* skip tutorial ([190ae71](https://github.com/coder/balatrobot/commit/190ae714c879baefbbf91fa9292ebd41e91a89b6))
* spelling for `debuf` to `debuff` ([e18ebfe](https://github.com/coder/balatrobot/commit/e18ebfe021611c3a381b75c1c99033552458cc7f))
* tmp fix for 8k luasocket buffer size ([#103](https://github.com/coder/balatrobot/issues/103)) ([d6f6cde](https://github.com/coder/balatrobot/commit/d6f6cdee29a2eaf861bee870947a225454b60cfc))
* update `debuff` name in game state ([d2a4769](https://github.com/coder/balatrobot/commit/d2a4769299d442d9ce2ad362cf50187f0ac17601))
* **utils:** check if GAME is nil in get_game_state ([d714c83](https://github.com/coder/balatrobot/commit/d714c837594165dc3dd7429d203416fc16cb9462))
* **utils:** prevent UI-related keys from being sanitized ([d37c2aa](https://github.com/coder/balatrobot/commit/d37c2aa3f3414e12ee0e6b26263601e6f3a1b2fd))
* validate that index is an integer ([e9ccc62](https://github.com/coder/balatrobot/commit/e9ccc62466eb1cc5b5c557051a11b5c5d6bdbc25))


### Documentation

* add api-protocol page to the docs ([11a7971](https://github.com/coder/balatrobot/commit/11a79715dd1a8416d80a68f0acdb1cc44203d41b))
* add audio option to docs for contributing ([045bcf7](https://github.com/coder/balatrobot/commit/045bcf71bae2f9a12ab483c6dc00ebb680f79120))
* add badges to readme ([fdfdb7d](https://github.com/coder/balatrobot/commit/fdfdb7d003474658d5fe5aa23e442d9671531567))
* add balatro documentation as git submodule ([5275d1c](https://github.com/coder/balatrobot/commit/5275d1caae582e796ffcd1d54c49dedb51a5e430))
* add CLAUDE.md with development guidelines and commands ([be7898e](https://github.com/coder/balatrobot/commit/be7898e1a231d762773b3f26ed6f31edd39e0c98))
* add comprehensive BalatroBot Python API reference ([548c0c3](https://github.com/coder/balatrobot/commit/548c0c3a6470186f6eb3b1a65fac7d3383d23abd))
* add comprehensive logging systems documentation ([b09d830](https://github.com/coder/balatrobot/commit/b09d8302cd5ca536f4aee0297326e534d36553db))
* add contributing.md ([b149388](https://github.com/coder/balatrobot/commit/b149388c2c32858f797d46cb8d11ebc622eb58f3))
* add dev env setup to bot-development.md ([f8a5b49](https://github.com/coder/balatrobot/commit/f8a5b4910a84a4d8a927cabe5a835d6c01a91065))
* add docs generated by llm ([1f5ef80](https://github.com/coder/balatrobot/commit/1f5ef80927858ef8a226dd233a0f0216990bf9d9))
* add homepage to docs ([77df9d6](https://github.com/coder/balatrobot/commit/77df9d636a0e99dc6de19bb06ba8002398077318))
* add log_path parameter to start_run ([4c74244](https://github.com/coder/balatrobot/commit/4c742449832cc49500ecbd7c1084a301170ac827))
* add logo configuration to mkdocs theme ([7ba1413](https://github.com/coder/balatrobot/commit/7ba14135b54a5c77ed3c40d12edfef2ab2925ad8))
* add MIT license ([6ee693c](https://github.com/coder/balatrobot/commit/6ee693c5d2ae703e712a9e4b9cf38edd8a6202c7))
* add pre-1.0 development warnings to README and docs ([3d70496](https://github.com/coder/balatrobot/commit/3d704966b42eecbd20a9e031905bdda0d45b2196))
* add project link to readme ([bddbad1](https://github.com/coder/balatrobot/commit/bddbad1b87a593940716452d058be20055a8ea81))
* add rearrange consumables to protocol api ([d1ec66f](https://github.com/coder/balatrobot/commit/d1ec66f3d274f330336eeef565a24a2ca9854909))
* add sell consumable endpoint to protocol-api.md ([209b0d8](https://github.com/coder/balatrobot/commit/209b0d8c4519090d1a1bfdc4db580c372f0cebc4))
* add sell joker to protocol-api.md ([ce99b11](https://github.com/coder/balatrobot/commit/ce99b11f7b7ac8c82158d496133ece055f6d1a8c))
* add use_consumable to protocol-api.md ([20915c7](https://github.com/coder/balatrobot/commit/20915c76ee152cccf059810ad4f78a5125b5dbaa))
* **api:** add standardized error codes and improve formatting ([5ca9813](https://github.com/coder/balatrobot/commit/5ca981363f2c26d4c11766d93571feb1ee4cc59b))
* **api:** add TODO comment for additional shop actions ([34071a2](https://github.com/coder/balatrobot/commit/34071a26ecc1624c0beefab1ae5a3279a4610575))
* **api:** refactor API protocol documentation for TCP implementation ([411268b](https://github.com/coder/balatrobot/commit/411268b7d25803ac8b307de8b163bd9b42559b8e))
* **bot:** init version for new balatrobot python package ([a29996e](https://github.com/coder/balatrobot/commit/a29996e21f59bfba97b90d40cd38d3ee48e1f21a))
* clean up formatting and mkdocs configuration ([4ec6e21](https://github.com/coder/balatrobot/commit/4ec6e218dd14ff92301685dc190c8d73a9878b70))
* configure mkdocs-llmstxt plugin for LLM-friendly documentation ([aaf9b38](https://github.com/coder/balatrobot/commit/aaf9b38b9a44d985602e9f2620d78db574539034))
* **dev:** add configuration system documentation ([16933cd](https://github.com/coder/balatrobot/commit/16933cd765b7c1d1887d0e9fc3c01098c25dc1ce))
* **dev:** clarify commit command formatting guidelines ([12130f2](https://github.com/coder/balatrobot/commit/12130f24c1262c4e8625d2468ea5522e46d9d351))
* **dev:** improve CLAUDE.md development commands and testing guidance ([2883a6d](https://github.com/coder/balatrobot/commit/2883a6d7faa6ade21936322e2890277b8baef1ab))
* **dev:** improve code documentation and comments ([b06c259](https://github.com/coder/balatrobot/commit/b06c259912b17cf246509a251f2bb7c776798804))
* **dev:** refine commit command workflow instructions ([c3340e6](https://github.com/coder/balatrobot/commit/c3340e6b00f6b29fd68993f224ff40337e2181d6))
* **dev:** update commit command co-author handling ([b554b44](https://github.com/coder/balatrobot/commit/b554b442daf3b686bbc28cfb46eed47ef1581555))
* **dev:** update commit command scope and co-author docs ([c089ff5](https://github.com/coder/balatrobot/commit/c089ff580ef70e485c3a8599eba4d1f6c121b20e))
* **dev:** update test suite metrics after shop API addition ([8c49a7d](https://github.com/coder/balatrobot/commit/8c49a7d9197dcb6042de550f3ddc489f092be440))
* **dev:** update test suite metrics in CLAUDE.md ([cc5b159](https://github.com/coder/balatrobot/commit/cc5b159c391dbfd2876bd2421cfb957eb98d4aad))
* **dev:** update test suite statistics ([dcf44fe](https://github.com/coder/balatrobot/commit/dcf44fe60cb1001a2239395a689ed53b9ad50980))
* enhance mkdocs config ([8a1714e](https://github.com/coder/balatrobot/commit/8a1714efe5a0ed2eeb3aa96ebde617cfd24a78cb))
* expand documentation with new references and best practices ([f4f6003](https://github.com/coder/balatrobot/commit/f4f6003cd4c0d7af1aa89b67ec44ae60fe228ca4))
* fix english grammar ([d14d9b2](https://github.com/coder/balatrobot/commit/d14d9b2d10cc7c3a1866f9900f2d419b8b2eebd4))
* fix mkdocs palette configuration format ([0756cd3](https://github.com/coder/balatrobot/commit/0756cd333861ec2d1fab71471cb9807356a64d08))
* improve bot-development page ([987e7eb](https://github.com/coder/balatrobot/commit/987e7eb0bbff3a912ccce9da250a2aab77faab90))
* improve MkDocs API documentation formatting ([7a537c2](https://github.com/coder/balatrobot/commit/7a537c21bd11dcfb94c21e028458555014325511))
* remove content from troubleshooting ([8f454b4](https://github.com/coder/balatrobot/commit/8f454b4715796df9f965edc9d7687de09f1776e7))
* remove emoji from docs ([b5acd72](https://github.com/coder/balatrobot/commit/b5acd722f2ec3fe8c07fc8e498ac3429b726234f))
* remove empty troubleshooting page and references ([b69d2ed](https://github.com/coder/balatrobot/commit/b69d2ed5bcc4179f873a4863abdd7c71fcb02d4f))
* remove legacy content in the README ([42cbde3](https://github.com/coder/balatrobot/commit/42cbde3b3de9c251bced3a0f92c6a29be5ca248e))
* remove legacy pages from mkdocs.yml ([2947b32](https://github.com/coder/balatrobot/commit/2947b32d7647cb71c4a742fb4a026ee705e8f4f2))
* remove legacy pages from the docs ([53cb13b](https://github.com/coder/balatrobot/commit/53cb13ba2dd033f58d267b1175a423ffc07cbf28))
* remove pre-1.0 notice ([4c232d0](https://github.com/coder/balatrobot/commit/4c232d01568b311860aba5b619ec5cbc4b2303df))
* remove redundant commands and refine existing ones ([a1e4d07](https://github.com/coder/balatrobot/commit/a1e4d070e9279f75681a45b836679093596c893c))
* remove table of contents from md files ([249ec7e](https://github.com/coder/balatrobot/commit/249ec7e99feeff0ba3bf5228017fcd088618ea4a))
* renamed log file and provide suggestion for Timeout errors ([ce6aa6d](https://github.com/coder/balatrobot/commit/ce6aa6d67fabc146a75805173a5044f776fed70c))
* replace troubleshooting with LLM documentation links on homepage ([b632077](https://github.com/coder/balatrobot/commit/b6320776ffbea2c8ba21a413261edc45bfa13cde))
* restructure documentation and configure mkdocstrings ([e89e34a](https://github.com/coder/balatrobot/commit/e89e34ab3d2cd5355148c584422a70a2bde68c16))
* simplify docs and add mermaid diagrams ([5fca88c](https://github.com/coder/balatrobot/commit/5fca88c9efd22c964eda1c6bb8adc9854f661ef1))
* simplify the contributing guide ([b3a729b](https://github.com/coder/balatrobot/commit/b3a729bdad7200e58089ee146ed6f94c2fb22c46))
* tmp fix for line numbers in code blocks ([939146a](https://github.com/coder/balatrobot/commit/939146a242fd4dad65c3eb3acd6ff6a649d32a47))
* update API documentation page titles ([ab79ef3](https://github.com/coder/balatrobot/commit/ab79ef3921c1f18b171f0a31b2f33f930e09a347))
* update badges in readme ([1353177](https://github.com/coder/balatrobot/commit/1353177c0926e652fefb049ba275edcab963a561))
* update balatrobot api with new models ([d611270](https://github.com/coder/balatrobot/commit/d611270d80d8f9b4806353470662135374819cc2))
* update CLAUDE.md with new make commands ([0f6c1e6](https://github.com/coder/balatrobot/commit/0f6c1e65bfce47d79d6d9c4dc4a10b1e01e59afc))
* update CLAUDE.md with test prerequisites and workflow ([f7436e0](https://github.com/coder/balatrobot/commit/f7436e01175c9ad22aaf95a7c86e401ec1162886))
* update contributing.md with new instructions for running tests in parallel ([44306dd](https://github.com/coder/balatrobot/commit/44306dd2ef41ba460eece0f5eed325b795f61a3f))
* update docs themes ([6059519](https://github.com/coder/balatrobot/commit/6059519b30849341fda3be73f960f729b5acaeb7))
* update docs/protocol-api.md with new sign for rearrange_hand ([6eff295](https://github.com/coder/balatrobot/commit/6eff29597a24d8cddc73f4344769216abf2df55a))
* update installation guide ([6afc3cd](https://github.com/coder/balatrobot/commit/6afc3cd4235d37ead4bf4c12a3c576a985942582))
* update links the from S1M0N38 to coder ([7b77fae](https://github.com/coder/balatrobot/commit/7b77faebf00030e6c4390062a89f5cd8f04f58fc))
* update README ([325dd20](https://github.com/coder/balatrobot/commit/325dd205ae6a35b37c869b8c238eecf3e072c3b1))
* update README.md with docs and contributors ([ba2c9da](https://github.com/coder/balatrobot/commit/ba2c9da6a956d65aa1eef8c53af86e1c33f9686f))
* update the path of the example bot ([023dbb0](https://github.com/coder/balatrobot/commit/023dbb0a4af28e7cdf170981e3ceb0a9f4ebd1f8))
* updpate bot-development docs page ([c687417](https://github.com/coder/balatrobot/commit/c6874176334b6e50edea30b2fc08bd2270563e38))
* use mkdocs admonition for warning ([11a0b0e](https://github.com/coder/balatrobot/commit/11a0b0e017df8565a694c2fa78320af3addc6703))

## [0.5.0](https://github.com/S1M0N38/balatrobot/compare/v0.4.1...v0.5.0) (2025-07-17)


### Features

* **api:** add hands_left to current_round game state ([79cec38](https://github.com/S1M0N38/balatrobot/commit/79cec3832a679215fea5d77f83507ce2e611a643))
* **bot:** add TCP-based replay bot for JSONL files ([b5b6cf8](https://github.com/S1M0N38/balatrobot/commit/b5b6cf8869c374c38b036353e5a81f8ded1a3b69))
* **log:** add JSONLLogEntry model and flexible arguments field ([3e8307a](https://github.com/S1M0N38/balatrobot/commit/3e8307a22277470b0627b1129149303b9f672ce5))
* **log:** add logging to BalatroClient connection and API calls ([3776c9c](https://github.com/S1M0N38/balatrobot/commit/3776c9c58eae1971393b8e738f6454e87ee2ba83))


### Bug Fixes

* **api:** add seed warning for non-reproducible runs ([b996f45](https://github.com/S1M0N38/balatrobot/commit/b996f45ff41252fa91fdb341c1f1c96b93b73712))
* **api:** prevent skipping Boss blind in skip_or_select_blind ([dc66e7e](https://github.com/S1M0N38/balatrobot/commit/dc66e7e75aeaaaf6cd9b32c30c424688a40ab548))
* **client:** make arguments optional in send_message ([56419f5](https://github.com/S1M0N38/balatrobot/commit/56419f55c6a87e9fc74b5bc10ed6dfd1b4890bb2))


### Documentation

* add comprehensive logging systems documentation ([b09d830](https://github.com/S1M0N38/balatrobot/commit/b09d8302cd5ca536f4aee0297326e534d36553db))
* clean up formatting and mkdocs configuration ([4ec6e21](https://github.com/S1M0N38/balatrobot/commit/4ec6e218dd14ff92301685dc190c8d73a9878b70))
* improve MkDocs API documentation formatting ([7a537c2](https://github.com/S1M0N38/balatrobot/commit/7a537c21bd11dcfb94c21e028458555014325511))

## [0.4.1](https://github.com/S1M0N38/balatrobot/compare/v0.4.0...v0.4.1) (2025-07-14)


### Documentation

* configure mkdocs-llmstxt plugin for LLM-friendly documentation ([aaf9b38](https://github.com/S1M0N38/balatrobot/commit/aaf9b38b9a44d985602e9f2620d78db574539034))
* remove empty troubleshooting page and references ([b69d2ed](https://github.com/S1M0N38/balatrobot/commit/b69d2ed5bcc4179f873a4863abdd7c71fcb02d4f))
* replace troubleshooting with LLM documentation links on homepage ([b632077](https://github.com/S1M0N38/balatrobot/commit/b6320776ffbea2c8ba21a413261edc45bfa13cde))
* update API documentation page titles ([ab79ef3](https://github.com/S1M0N38/balatrobot/commit/ab79ef3921c1f18b171f0a31b2f33f930e09a347))

## [0.4.0](https://github.com/S1M0N38/balatrobot/compare/v0.3.0...v0.4.0) (2025-07-14)


### Features

* **api:** add comprehensive error handling and validation system ([c00eca4](https://github.com/S1M0N38/balatrobot/commit/c00eca477caee4a2b3a816db4884e425eb85cded))
* **bot:** add standardized error codes enum ([2c9fdaa](https://github.com/S1M0N38/balatrobot/commit/2c9fdaaf1e0cfbfbb5586e633c0fa8cd97db496d))
* **bot:** replace Bot ABC with structured API client ([3a70fde](https://github.com/S1M0N38/balatrobot/commit/3a70fdef70a5647732155bc2608d37f5fdc10182))
* **examples:** update example bot to use new client API ([73bf5b7](https://github.com/S1M0N38/balatrobot/commit/73bf5b7c19e15a65968de5c273b51754ffba2419))
* **tests:** add TCP client support to test infrastructure ([ff935f3](https://github.com/S1M0N38/balatrobot/commit/ff935f3f39b873e97a580f02fe8204f2e03565d3))


### Bug Fixes

* **api:** add card count validation to play_hand_or_discard function ([0072a0e](https://github.com/S1M0N38/balatrobot/commit/0072a0e8fbc078bde347f4bd5f1b771a911da4e8))
* **api:** add event queue threshold check to start_run condition ([ea210ed](https://github.com/S1M0N38/balatrobot/commit/ea210ed47021f90106248bbf8cced3e9f9e7c878))
* **api:** correct socket type references from UDP to TCP ([149d314](https://github.com/S1M0N38/balatrobot/commit/149d3148184561b86562dac2e4604ac117fbf0ec))
* **ci:** correct YAML indentation in deploy docs workflow ([ca2d797](https://github.com/S1M0N38/balatrobot/commit/ca2d797b4c73dfb6cb869af995a0caaf2913bbad))
* **dev:** remove --check flag from mdformat command ([3f710b8](https://github.com/S1M0N38/balatrobot/commit/3f710b8ba13a79432284732ee420e778e45915ac))


### Documentation

* add comprehensive BalatroBot Python API reference ([548c0c3](https://github.com/S1M0N38/balatrobot/commit/548c0c3a6470186f6eb3b1a65fac7d3383d23abd))
* **api:** add standardized error codes and improve formatting ([5ca9813](https://github.com/S1M0N38/balatrobot/commit/5ca981363f2c26d4c11766d93571feb1ee4cc59b))
* **api:** refactor API protocol documentation for TCP implementation ([411268b](https://github.com/S1M0N38/balatrobot/commit/411268b7d25803ac8b307de8b163bd9b42559b8e))
* **bot:** init version for new balatrobot python package ([a29996e](https://github.com/S1M0N38/balatrobot/commit/a29996e21f59bfba97b90d40cd38d3ee48e1f21a))
* **dev:** improve CLAUDE.md development commands and testing guidance ([2883a6d](https://github.com/S1M0N38/balatrobot/commit/2883a6d7faa6ade21936322e2890277b8baef1ab))
* **dev:** update test suite statistics ([dcf44fe](https://github.com/S1M0N38/balatrobot/commit/dcf44fe60cb1001a2239395a689ed53b9ad50980))
* restructure documentation and configure mkdocstrings ([e89e34a](https://github.com/S1M0N38/balatrobot/commit/e89e34ab3d2cd5355148c584422a70a2bde68c16))

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
