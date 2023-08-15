import json, os, time, colorama
from colorama import Fore, Style

colorama.init()
print(f'{Fore.LIGHTRED_EX}UbiArt tpl2tape by Itay.{Style.RESET_ALL}')

class Util:
    def loadJson(path):
        try:
            res = json.load(open(path, encoding='utf-8'))
        except:
            res = json.loads(open(path, encoding='utf-8').read()[:-1])
        return res
    
    def saveJson(path, content):
        open(path , 'wb').write(json.dumps(content, separators=(',', ':')).encode() + b'\x00')

    def error(msg, toExit):
        print(f'{Fore.RED} [ERROR]: {msg} {Style.RESET_ALL}')
        time.sleep(5)
        if toExit:
            exit()
    
    def printBlock(block):
        print(f'{Fore.BLUE}- [BLOCK]:{Style.RESET_ALL}{Fore.LIGHTGREEN_EX} {block}{Style.RESET_ALL}')

    def logging(msg):
        print(f'{Fore.LIGHTYELLOW_EX}- [LOGGING]: {Style.RESET_ALL}{Fore.LIGHTGREEN_EX}{msg}{Style.RESET_ALL}')

    def getFilename(path: str):
        return path.split('/')[-1]

def tpl2tape(filename):
    filePath = os.path.join('input', filename)
    if not os.path.isfile(filePath):
        return 
    print(f'{Fore.MAGENTA}---- {filename} ----{Style.RESET_ALL}')
    tpl = Util.loadJson(filePath)
    JD_BlockFlowTemplate = tpl['COMPONENTS'][0]['BlockDescriptorVector']
    MU_CodeName = JD_BlockFlowTemplate[0]['BaseBlock']['songName']
    tape = {"__class":"Tape","Clips":[],"TapeClock":0,"TapeBarCount":1,"FreeResourcesAfterPlay":0,"MapName":MU_CodeName,"SoundwichEvent":""}
    for block in JD_BlockFlowTemplate:
        startTime = block['BaseBlock']['frstBeat'] * 24
        for AlternativeBlock in block['AlternativeBlocks']:
            ALT_StartTime = AlternativeBlock['frstBeat'] * 24
            ALT_EndTime = AlternativeBlock['lastBeat'] * 24
            AlternativeBlock_mapName = AlternativeBlock['songName']
            try:
                AlternativeBlock_DanceTape = Util.loadJson(os.path.join('input', 'tmls', f'{AlternativeBlock_mapName}_tml_dance.dtape.ckd'))
            except:
                Util.error(f'Couldnt find {AlternativeBlock_mapName} DanceTape (dtape)', True)
            Util.printBlock(AlternativeBlock_mapName)
            for clip in AlternativeBlock_DanceTape['Clips']:
                if clip['StartTime'] >= ALT_StartTime and clip['StartTime'] <= ALT_EndTime:
                    clip['StartTime'] -= ALT_StartTime
                    clip['StartTime'] += startTime
                    if clip['__class'] == 'MotionClip':
                        clip['ClassifierPath'] = f"world/maps/{MU_CodeName}/timeline/moves/{Util.getFilename(clip['ClassifierPath'])}".lower()
                    elif clip['__class'] == 'PictogramClip':
                        clip['PictoPath'] = f"world/maps/{MU_CodeName}/timeline/pictos/{Util.getFilename(clip['PictoPath'])}".lower()
                    tape['Clips'].append(clip)
    tape['Clips'].sort(key=lambda x: x["StartTime"]) # sorting clips by their StartTime
    outputPath = f'output/{MU_CodeName}_tml_dance.dtape.ckd'.lower()
    Util.saveJson(outputPath, tape)
    print(f'{Fore.LIGHTCYAN_EX}-- [{outputPath}] has been saved with {len(tape["Clips"])} clips --{Style.RESET_ALL}')

def main():
    for filename in os.listdir('input'):
        try:
            tpl2tape(filename)
        except:
            Util.error(f'Something went wrong while processing {filename}.', True)

    print(f'{Fore.LIGHTYELLOW_EX}Done converting all maps!{Style.RESET_ALL}')

if __name__ == '__main__':
    main()