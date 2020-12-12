# anime-dl
CLI to download anime episodes from anime websites like GoGoAnime.

Features:
  - Download anime from:
    - [GoGoAnime]
    - [HorribleSubs] (Requires [WeeChat] installed). RIP.
    - [4Anime]
    - [Animekisa]
    - [SubsPlease] (Requires [WeeChat] installed).
  - Support resume download.

Examples:
  - Download naruto episodes from 1 to 220
    ```console
    $ anime_dl.py --url https://www.gogoanime1.com/watch/naruto --list 1-220
    ```
    
  - Download naruto shippuuden episodes from 1 to 500, but skipping filler episodes. Filler episodes are listed at https://www.animefillerlist.com/shows/naruto-shippuden
    ```console
    $ anime_dl.py --url https://www.gogoanime1.com/watch/naruto-shippuuden --list "1-500" --filler "28, 57-71, 91-112, 144-151, 170-171, 176-196, 223-242, 257-260, 271, 279-281, 284-295, 303-320, 347-361, 376-377, 389-390, 394-413, 416, 422-423, 427-450, 464-469, 480-483" --skip-filler
    ```
[weechat]: <https://weechat.org>
[GoGoAnime]: <https://www.gogoanime1.com>
[HorribleSubs]: <https://horriblesubs.info>
[4Anime]: <https://4anime.to>
[Animekisa]: <https://animekisa.tv>
[SubsPlease]: <https://subsplease.org>
