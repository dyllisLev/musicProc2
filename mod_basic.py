import base64
import random
from io import BytesIO

from PIL import Image
from support import SupportDiscord
from tool import ToolNotify

from .musicProc2 import musicProc2
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
            mp = musicProc2(P)
            ret = mp.tagUpdate(param)
        elif command == 'shazam_tag':
            None
            mp = musicProc2(P)
            ret = mp.shazam_tag(param)
           
        return jsonify(ret)

    def scheduler_function(self):
        logger.debug(f'scheduler_function IN')
        try:
            
            ret = self.do_action()  # mode='test_info' / 'test_buy' / 'buy'(기본)
           
            msg = "음악정리 끝!"
            ToolNotify.send_message(msg, 'musicProc')
        except Exception as e:
            logger.error(f'Exception:{str(e)}')
            logger.error(traceback.format_exc())

    def do_action(self):
        logger.debug(f'do_action IN')
        try:
            ret = {'status': None}
            mp = musicProc2(P)
            mp.run()
            return ret
        
        except Exception as e:
            logger.error(f'Exception:{str(e)}')
            logger.error(traceback.format_exc())
            ret['status'] = 'fail'
            ret['log'] = str(traceback.format_exc())
        finally:
            # lotto.driver_quit()
            P.logger.debug(d(ret))
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
