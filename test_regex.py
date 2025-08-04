import re
url = 'https://botsmother.com/api/command/OTMx/NzY0Ng==?tgWebAppStartParam=962731079#tgWebAppData=user%3D%257B%2522id%2522%253A7948727427%252C%2522first_name%2522%253A%2522Ana%2522%252C%2522last_name%2522%253A%2522Baba%2522%252C%2522language_code%2522%253A%2522ar%2522%252C%2522allows_write_to_pm%2522%253Atrue%252C%2522photo_url%2522%253A%2522https%253A%255C%252F%255C%252Ft.me%255C%252Fi%255C%252Fuserpic%255C%252F320%255C%252FTUZOu3ms_T7-g1QACIbQ5O3XG_3XUC9ND-XqIofA274XEh2w5y8ZKWCX6ljrb5dW.svg%2522%257D%26chat_instance%3D-8020935930157437618%26chat_type%3Dsender%26start_param%3D962731079%26auth_date%3D1754295951%26signature%3DNobjn9eEaKlAUqQjrcM24P4P31bvmhl5jyWlkEHHlrRAwkxK2ecYfRF6DTr93SE6A1QmllFo-nRXB0eJGQKxBw%26hash%3D70be114ad13498c3a8f761276b5f67d33b955939f976edb68154e4d451a8b688'
match = re.search(r'tgWebAppData=([^&]+)', url)
if match:
    print('Found data:', match.group(1)[:100] + '...')
    print('Full data length:', len(match.group(1)))
else:
    print('No match found')
