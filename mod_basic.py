import base64
import random
from io import BytesIO

from PIL import Image
from support import SupportDiscord
from tool import ToolNotify

from .musicProc import musicProc
from .model import ModelMusicItem
from .setup import *


class ModuleBasic(PluginModuleBase):
    
    def __init__(self, P):
        super(ModuleBasic, self).__init__(P, name='basic', first_menu='setting', scheduler_desc="자동 음악정리")
        self.db_default = {
         
            f'db_version' : '1',
            f'{self.name}_auto_start': 'False',
            f'{self.name}_interval': '0 8 * * *',
            f'{self.name}_db_delete_day': '30',
            f'{self.name}_db_auto_delete': 'False',
            f'{P.package_name}_item_last_list_option': '',
            
            f'download_path' : '',
            f'proc_path' : '',
            f'err_path' : '',
            f'maxCost' : '200',
            f'singleCost' : '0',
            f'folderStructure' : '%artist%/%album%/',
            f'fileRenameSet' : '%track% - %title%',
            f'interval' : '5',
            f'isEncoding' : 'True',
            f'isEncodingType' : 'MP3,M4A',
            f'genreExc' : '',
            f'schedulerInterval' : '60',
            f'auto_start' : 'False',
            f'emptyFolderDelete' : 'False',
            f'notMp3delete' : 'False',
            f'fileRename' : 'False',
            f'isDupeDel' : 'False',
            f'isTagUpdate' : 'False',
            f'isShazam' : 'False'
            
        }
        self.web_list_model = ModelMusicItem

    def process_menu(self, sub, req):
        logger.debug(f'process_menu IN : %s'%sub)
        arg = P.ModelSetting.to_dict()
        if sub == 'setting':
            arg['is_include'] = F.scheduler.is_include(self.get_scheduler_name())
            arg['is_running'] = F.scheduler.is_running(self.get_scheduler_name())
        return render_template(f'{P.package_name}_{self.name}_{sub}.html', arg=arg)
    
    def process_command(self, command, arg1, arg2, arg3, req):
        logger.debug(f'process_command IN %s'%command)


        param = self.parse_params(arg1)
        logger.debug(f'process_command IN %s'%arg1)
        logger.debug(f'process_command IN %s'%param)

        ret = {'ret': 'success'}
        if command == 'update_tag':
            None
            mp = musicProc(P)
            ret = mp.tagUpdate(param)
           
            # return jsonify(ret)

            # data = self.do_action(mode=command)
            # if ret['status'] == 'fail':
            #     ret['modal'] = d(data['data'])
            #     ret['title'] = '에러'
            #     ret['data'] = data
            # else:
            #     ret['modal'] = f"예치금 : {data['deposit']}"
            #     ret['modal'] += f"\n이미 구입 : {data['history']['count']}건 (미추첨)"
            #     ret['modal'] += f"\n가능 : {data['available_count']}건"
            #     if 'buy' in data:
            #         ret['modal'] += f"\n회차 : {data['buy']['round']}"
            #     ret['title'] = "테스트"
            #     ret['data'] = data
        return jsonify(ret)

    def scheduler_function(self):
        logger.debug(f'scheduler_function IN')
        try:
            
            # noti_mode = P.ModelSetting.get('notify_mode')
            # notify = False
            ret = self.do_action()  # mode='test_info' / 'test_buy' / 'buy'(기본)
            
            # img_bytes = None
            # img_url = None
            
            # msg = '로또'
            # msg += f"\n예치금 : {ret['deposit']}"
            # msg += f"\n구매가능 : {ret['available_count']}"

            # if ret['status'] == 'NOT_AVAILABLE_COUNT':
            #     msg += "\n구매 가능 건수가 없어 종료"
            # elif ret['status'] == 'ALREADY_THIS_WEEK_BUY':
            #     msg += "\n이미 이번 주 구매"
            # elif ret['status'] == 'NOT_AVAILABLE_MONEY':
            #     msg += "\n예치금 부족으로 종료"
            #     if noti_mode == 'real_buy':
            #         notify = True
            # else:
            #     msg += f"\n구매 수 : {len(ret['buy']['buy_list'])}"
            #     msg += f"\n회차 : {ret['buy']['round']}"

            # if 'buy' in ret and len(ret['buy']['buy_list']) > 0:
            #     img_bytes = base64.b64decode(ret['buy']['screen_shot'])
            #     filepath = os.path.join(F.config['path_data'], 'tmp', f"proxy_{str(time.time())}.png")
            #     img = Image.open(BytesIO(img_bytes))
            #     img.save(filepath)
            #     img_url = SupportDiscord.discord_proxy_image_localfile(filepath)
            #     if noti_mode == 'real_buy':
            #         notify = True
            #     db_item = ModelLottoItem()
            #     db_item.round = ret['buy']['round']
            #     db_item.count = len(ret['buy']['buy_list'])
            #     db_item.data = ret
            #     db_item.img = img_url
            #     db_item.save()
           
            # if noti_mode == 'always':
            #     notify = True
            # elif noti_mode == 'none':
            #     notify = False
            
            # if notify:
            msg = "음악정리 끝!"
            ToolNotify.send_message(msg, 'musicProc')
        except Exception as e:
            logger.error(f'Exception:{str(e)}')
            logger.error(traceback.format_exc())

    def do_action(self, mode="buy"):
        logger.debug(f'do_action IN')
        try:
            ret = {'status': None}
            mp = musicProc(P)
            mp.run()
            return ret
        
            # lotto.driver_init(P.ModelSetting.get('driver_mode'), P.ModelSetting.get_bool('driver_local_headless'), P.ModelSetting.get('driver_remote_url'))
            # lotto.login(P.ModelSetting.get('user_id'), P.ModelSetting.get('user_passwd'))
            # ret['deposit'] = lotto.check_deposit()
            # ret['history'] = lotto.check_history()
            # stream = BytesIO(ret['history']['screen_shot'])
            # img = Image.open(stream)
            # img.save(stream, format='png')
            # ret['history']['screen_shot'] = base64.b64encode(stream.getvalue()).decode() 
            # ret['available_count'] = 5 - ret['history']['count']
            # if mode == 'test_info':
            #     return ret
            
            # buy_data = self.get_buy_data()
            # if ret['available_count'] == 0:
            #     ret['status'] = 'NOT_AVAILABLE_COUNT'
            # elif P.ModelSetting.get_bool('buy_mode_one_of_week') and ret['available_count'] != 5:
            #     ret['status'] = 'ALREADY_THIS_WEEK_BUY'
            # else:
            #     if min(len(buy_data), ret['available_count']) * 1000 > ret['deposit']:
            #         ret['status'] = 'NOT_AVAILABLE_MONEY'

            # if len(buy_data) > ret['available_count']:
            #     buy_data = buy_data[:ret['available_count']]

            # if ret['status'] is None:
            #     if mode == 'test_buy':
            #         ret['buy'] = lotto.buy_lotto(buy_data, dry=True)
            #     else:
            #         ret['buy'] = lotto.buy_lotto(buy_data)
            #     stream = BytesIO(ret['buy']['screen_shot'])
            #     img = Image.open(stream)
            #     img.save(stream, format='png')
            #     ret['buy']['screen_shot'] = base64.b64encode(stream.getvalue()).decode()
            # return ret
        except Exception as e:
            logger.error(f'Exception:{str(e)}')
            logger.error(traceback.format_exc())
            ret['status'] = 'fail'
            ret['log'] = str(traceback.format_exc())
        finally:
            # lotto.driver_quit()
            P.logger.debug(d(ret))
        return ret

    @staticmethod
    def get_buy_data():
        def auto():
            ret = []
            while len(ret) < 6:
                tmp = str(random.randint(1, 45))
                if tmp not in ret:
                    ret.append(tmp)
            return ret

        data = P.ModelSetting.get_list('buy_data')
        ret = []
        plugin_auto = auto()
        for item in data:
            if item.startswith('plugin_auto'):
                ret.append(f"manual : {','.join(plugin_auto)}")
            else:
                ret.append(item)
        P.logger.info(d(ret))
        return ret
    def parse_params(self, input_string):
        # 문자열을 '&'로 split하여 각 key=value 쌍으로 분리
        key_values = input_string.split('&')[1:]

        # key=value 쌍을 dict 형태로 변환
        params = {}
        for key_value in key_values:
            key, value = key_value.split('=')
            params[key] = value

        return params
