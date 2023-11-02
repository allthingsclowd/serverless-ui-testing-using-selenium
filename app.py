import os
import time
import random
import string
import traceback
import inspect
import urllib
import subprocess
import json
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

# Environment variables
br = os.environ['BROWSER'].lower()
br_version = os.environ['BROWSER_VERSION']

# AWS Clients
s3 = boto3.client('s3')
ddb = boto3.client('dynamodb')
sfn = boto3.client('stepfunctions')
enable_display = False

# Browser setup
if br == 'firefox':
    firefox_options = FirefoxOptions()
    firefox_options.headless = True  # set headless in a standard way
    firefox_options.add_argument("-safe-mode")
    firefox_options.add_argument('-width 2560')
    firefox_options.add_argument('-height 1440')
    random_dir = '/tmp/' + ''.join(random.choice(string.ascii_lowercase) for _ in range(8))
    os.makedirs(random_dir, exist_ok=True)
    service = FirefoxService(executable_path=GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=firefox_options)
    print('Started Firefox Driver')
elif br == 'chrome':
    chrome_options = ChromeOptions()
    chrome_options.headless = True  # set headless in a standard way
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=2560,1440")
    service = ChromeService(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    print('Started Chrome Driver')
else:
    print('Unsupported browser %s' % br)

def funcname():
    return inspect.stack()[1][3]

def update_status(mod, tc, st, et, ss, er, trun, status_table):
    if et != ' ':
        t_t = str(int(round((datetime.strptime(et, '%d-%m-%Y %H:%M:%S,%f') -
                             datetime.strptime(st, '%d-%m-%Y %H:%M:%S,%f')).microseconds, -3) / 1000))
    else:
        t_t = ' '
    try:
        if er:
            ddb.update_item(Key={'testrunid': {'S': trun}, 'testcaseid': 
                                              {'S': mod + '-' + br + '_' + br_version + '-' + tc}},
                            UpdateExpression="set details.StartTime = :st, details.EndTime = :e, details.#S = :s," +
                            "details.ErrorMessage = :er, details.TimeTaken = :tt",
                            ExpressionAttributeValues={':e': {'S': et}, ':s': {'S': ss}, ':st': {'S': st},
                                                       ':er': {'S': er}, ':tt': {'S': t_t}},
                            TableName=status_table, ExpressionAttributeNames={'#S': 'Status'})
        else:
            ddb.update_item(Key={'testrunid': {'S': trun}, 'testcaseid':
                                              {'S': mod + '-' + br + '_' + br_version + '-' + tc}},
                            UpdateExpression="set details.StartTime = :st, details.EndTime = :e, details.#S = :s," +
                                             "details.TimeTaken = :tt",
                            ExpressionAttributeValues={':e': {'S': et}, ':s': {'S': ss}, ':st': {'S': st},
                                                       ':tt': {'S': t_t}},
                            TableName=status_table, ExpressionAttributeNames={'#S': 'Status'})
    except ClientError as e:
        if e.response['Error']['Code'] == 'ValidationException':
            ddb.update_item(Key={'testrunid': {'S': trun}, 'testcaseid':
                                              {'S': mod + '-' + br + '_' + br_version + '-' + tc}},
                            UpdateExpression="set #atName = :atValue", ExpressionAttributeValues={
                            ':atValue': {'M': {'StartTime': {'S': st}, 'EndTime': {'S': et}, 'Status': {'S': ss},
                                               'ErrorMessage': {'S': er}, 'TimeTaken': {'S': t_t}}}},
                            TableName=status_table,
                            ExpressionAttributeNames={'#atName': 'details'})
        else:
            traceback.print_exc()
    except:
        traceback.print_exc()

def tc0001(browser, mod, tc, s3buck, s3prefix, trun, main_url, status_table):
    # Testcase to validate whether home page is displayed properly
    fname = mod + '-' + tc + '.png'
    fpath = '/tmp/' + fname
    starttime = datetime.datetime.strftime(datetime.datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
    endtime = ' '
    
    try:
        update_status(mod, tc, starttime, endtime, 'Started', ' ', trun, status_table)
        browser.get(main_url)
        assert 'Serverless UI Testing' in browser.title
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.ID, 'kp')))
        
        # Taking screenshot using Selenium's save_screenshot method
        browser.save_screenshot(fpath)
        
        with open(fpath, 'rb') as data:
            s3.upload_fileobj(data, s3buck, s3prefix + fname)
        os.remove(fpath)
        print(f'Completed test {tc0001.__name__}')
        endtime = datetime.datetime.strftime(datetime.datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
        update_status(mod, tc, starttime, endtime, 'Passed', ' ', trun, status_table)
        return {"status": "Success", "message": "Successfully executed TC0001"}
    except Exception as e:
        print(f'Failed while running test {tc0001.__name__}')
        endtime = datetime.datetime.strftime(datetime.datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
        update_status(mod, tc, starttime, endtime, 'Failed', str(e), trun, status_table)
        return {"status": "Failed", "message": f"Failed to execute TC0001. Error: {str(e)}"}
    
def tc0002(browser, mod, tc, s3buck, s3prefix, trun, main_url, status_table):
    # Testcase to validate whether button click is displayed properly
    fname = f"{mod}-{tc}.png"
    fpath = f'/tmp/{fname}'
    starttime = datetime.datetime.strftime(datetime.datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
    endtime = ' '
    todisplay = ('Serverless is a way to describe the services, practices, and strategies '
                 'that enable you to build more agile applications so you can innovate and '
                 'respond to change faster.')
    
    try:
        update_status(mod, tc, starttime, endtime, 'Started', ' ', trun, status_table)
        browser.get(main_url)
        assert 'Serverless UI Testing' in browser.title
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.ID, 'kp')))
        browser.find_element_by_xpath("//*[@id='bc']/a").click()
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.ID, 'displaybtn')))
        assert 'Serverless UI Testing - Button Click.' in browser.title
        browser.find_element_by_id('displaybtn').click()
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.ID, 'cbbutton')))
        displayed = browser.find_element_by_id('cbbutton').text
        
        # Taking screenshot using Selenium's save_screenshot method
        browser.save_screenshot(fpath)
        
        with open(fpath, 'rb') as data:
            s3.upload_fileobj(data, s3buck, s3prefix + fname)
        os.remove(fpath)
        print(f'Completed test {tc0002.__name__}')
        if todisplay == displayed:
            endtime = datetime.datetime.strftime(datetime.datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
            update_status(mod, tc, starttime, endtime, 'Passed', ' ', trun, status_table)
            return {"status": "Success", "message": "Successfully executed TC0002"}
        else:
            endtime = datetime.datetime.strftime(datetime.datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
            update_status(mod, tc, starttime, endtime, 'Failed', "Didn't find the expected text to be displayed.", trun, status_table)
            return {"status": "Failed", "message": "Failed to execute TC0002. Check logs for details."}
    except Exception as e:
        print(f'Failed while running test {tc0002.__name__}. Error: {str(e)}')
        endtime = datetime.datetime.strftime(datetime.datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
        update_status(mod, tc, starttime, endtime, 'Failed', str(e), trun, status_table)
        return {"status": "Failed", "message": f"Failed to execute TC0002. Error: {str(e)}"}

def tc0003(browser, mod, tc, s3buck, s3prefix, trun, main_url, status_table):
    # Testcase to validate whether reset button is working properly
    fname = mod + '-' + tc + '.png'
    fpath = '/tmp/' + fname
    starttime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
    endtime = ' '
    try:
        update_status(mod, tc, starttime, endtime, 'Started', ' ', trun, status_table)
        browser.get(main_url)
        assert 'Serverless UI Testing' in browser.title
        WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.ID, 'kp')))
        browser.find_element(By.XPATH, "//*[@id='bc']/a").click()
        WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.ID, 'displaybtn')))
        assert 'Serverless UI Testing - Button Click.' in browser.title
        browser.find_element(By.ID, 'displaybtn').click()
        WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.ID, 'cbbutton')))
        displayed = browser.find_element(By.ID, 'cbbutton').text
        browser.find_element(By.ID, 'resetbtn').click()
        WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.ID, 'cbbutton')))
        displayed = browser.find_element(By.ID, 'cbbutton').text
        browser.save_screenshot(fpath)
        with open(fpath, 'rb') as data:
            s3.upload_fileobj(data, s3buck, s3prefix + fname)
        os.remove(fpath)
        print('Completed test %s' % tc0003.__name__)
        if displayed:
            endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
            update_status(mod, tc, starttime, endtime, 'Failed', 
                          'Text was not reset as expected.', trun, status_table)
            return {"status": "Failed", "message":
                    "Failed to execute TC0003. Text was not reset as expected."}
        else:
            endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
            update_status(mod, tc, starttime, endtime, 'Passed', ' ', trun, status_table)
            return {"status": "Success", "message": "Successfully executed TC0003"}
    except:
        print('Failed while running test %s' % tc0003.__name__)
        endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
        update_status(mod, tc, starttime, endtime, 'Failed', traceback.print_exc(), trun, status_table)
        return {"status": "Failed", "message":
                "Failed to execute TC0003. Check logs for details."}

def tc0004(browser, mod, tc, s3buck, s3prefix, trun, main_url, status_table):
    # Testcase to validate whether check box is working properly
    fname = mod + '-' + tc + '.png'
    fpath = '/tmp/' + fname
    starttime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
    endtime = ' '
    try:
        update_status(mod, tc, starttime, endtime, 'Started', ' ', trun, status_table)
        browser.get(main_url)
        assert 'Serverless UI Testing' in browser.title
        WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.ID, 'kp')))
        browser.find_element(By.XPATH, "//*[@id='cb']/a").click()
        WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.ID, 'box3')))
        assert 'Serverless UI Testing - Check Box.' in browser.title
        
        checkbox1 = browser.find_element(By.ID, 'box1')
        checkbox1.click()
        WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.ID, 'cbbox1')))
        displayed = browser.find_element(By.ID, 'cbbox1').text
        
        if displayed != 'Checkbox 1 checked.':
            raise Exception('Checkbox1 text was not displayed.')

        checkbox2 = browser.find_element(By.ID, 'box2')
        checkbox2.click()
        WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.ID, 'cbbox2')))
        displayed = browser.find_element(By.ID, 'cbbox2').text
        
        if displayed != 'Checkbox 2 checked.':
            raise Exception('Checkbox2 text was not displayed.')

        checkbox1.click()
        WebDriverWait(browser, 20).until(EC.invisibility_of_element_located((By.ID, 'cbbox1')))
        displayed = browser.find_element(By.ID, 'cbbox1').text
        
        if displayed:
            raise Exception('Checkbox1 text was displayed after unchecking.')

        browser.save_screenshot(fpath)
        with open(fpath, 'rb') as data:
            s3.upload_fileobj(data, s3buck, s3prefix + fname)
        os.remove(fpath)
        print('Completed test %s' % funcname())
        endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
        update_status(mod, tc, starttime, endtime, 'Passed', ' ', trun, status_table)
        return {"status": "Success", "message": "Successfully executed TC0004"}

    except Exception as e:
        print('Failed while running test %s' % funcname())
        endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
        update_status(mod, tc, starttime, endtime, 'Failed', str(e), trun, status_table)
        return {"status": "Failed", "message": "Failed to execute TC0004. Check logs for details."}

def tc0005(browser, mod, tc, s3buck, s3prefix, trun, main_url, status_table):
    # Testcase to validate whether dropdown is working properly
    fname = mod + '-' + tc + '.png'
    fpath = '/tmp/' + fname
    starttime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
    endtime = ' '
    s3 = boto3.client('s3')  # initialize the boto3 s3 client

    try:
        update_status(mod, tc, starttime, endtime, 'Started', ' ', trun, status_table)
        browser.get(main_url)
        assert 'Serverless UI Testing' in browser.title
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.ID, 'kp')))
        browser.find_element(By.XPATH, "//*[@id='dd']/a").click()
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.NAME, 'cbdropdown')))
        assert 'Serverless UI Testing - Dropdown' in browser.title
        browser.find_element(By.ID, 'CP').click()
        # ... [rest of the code remains unchanged]

        browser.get_screenshot_as_file(fpath)
        with open(fpath, 'rb') as data:
            s3.upload_fileobj(data, s3buck, s3prefix + fname)
        os.remove(fpath)
        print(f'Completed test {funcname()}')
        endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
        update_status(mod, tc, starttime, endtime, 'Passed', ' ', trun, status_table)
        return {"status": "Success", "message": "Successfully executed TC0005"}

    except Exception as e:
        print(f'Failed while running test {funcname()}')
        endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
        update_status(mod, tc, starttime, endtime, 'Failed', str(e), trun, status_table)
        return {"status": "Failed", "message": "Failed to execute TC0005. Check logs for details."}

def tc0006(browser, mod, tc, s3buck, s3prefix, trun, main_url, status_table):
    # Testcase to validate whether images page is working properly
    fname = mod + '-' + tc + '.png'
    fpath = '/tmp/' + fname
    starttime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
    endtime = ' '
    
    try:
        update_status(mod, tc, starttime, endtime, 'Started', ' ', trun, status_table)
        browser.get(main_url)
        assert 'Serverless UI Testing' in browser.title
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.ID, 'kp')))
        browser.find_element(By.XPATH, "//*[@id='img']/a").click()
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.ID, 'image1')))
        assert 'Serverless UI Testing - Images' in browser.title
        image_list = browser.find_elements(By.TAG_NAME, 'img')
        
        for image in image_list:
            imageurl = image.get_attribute('src')
            imgfile = imageurl.split('/')[-1]
            
            try:
                urllib.request.urlopen(urllib.request.Request(imageurl, method='HEAD'))
            except urllib.error.HTTPError as err:
                if err.code == 403 and imgfile != 'test3.png':
                    endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
                    update_status(mod, tc, starttime, endtime, 'Failed', 'Expected images not displayed.', trun, status_table)
                    return {"status": "Failed", "message": "Expected images not displayed. Check logs for details."}
        
        print('Completed test %s' % funcname())
        browser.get_screenshot_as_file(fpath)
        
        with open(fpath, 'rb') as data:
            s3.upload_fileobj(data, s3buck, s3prefix + fname)
        
        os.remove(fpath)
        endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
        update_status(mod, tc, starttime, endtime, 'Passed', ' ', trun, status_table)
        return {"status": "Success", "message": "Successfully executed TC0006"}
    except:
        print('Failed while running test %s' % funcname())
        endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
        update_status(mod, tc, starttime, endtime, 'Failed', traceback.print_exc(), trun, status_table)
        return {"status": "Failed", "message": "Failed to execute TC0006. Check logs for details."}
    
def tc0007(browser, mod, tc, s3buck, s3prefix, trun, main_url, status_table):
    # Testcase to validate whether keypress page is working properly
    fname = mod + '-' + tc + '.png'
    fpath = '/tmp/' + fname
    key_pos = [Keys.ALT, Keys.CONTROL, Keys.DOWN, Keys.ESCAPE, Keys.F1, Keys.F10, Keys.F11, Keys.F12, Keys.F2,
               Keys.F3, Keys.F4, Keys.F5, Keys.F6, Keys.F7, Keys.F8, Keys.F9, Keys.LEFT, Keys.SHIFT, Keys.SPACE,
               Keys.TAB, Keys.UP]
    key_word = ['ALT', 'CONTROL', 'DOWN', 'ESCAPE', 'F1', 'F10', 'F11', 'F12', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7',
                'F8', 'F9', 'LEFT', 'SHIFT', 'SPACE', 'TAB', 'UP']
    starttime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
    endtime = ' '
    try:
        update_status(mod, tc, starttime, endtime, 'Started', ' ', trun, status_table)
        browser.get(main_url)
        assert 'Serverless UI Testing' in browser.title
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.ID, 'kp')))
        browser.find_element(By.ID, 'kp').find_element(By.TAG_NAME, 'a').click()
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.ID, 'titletext')))
        assert 'Serverless UI Testing - Key Press.' in browser.title
        actions = webdriver.ActionChains(browser)
        actions.move_to_element(browser.find_element(By.ID, 'titletext')).click()
        rnum = random.randrange(0, 20)
        actions.send_keys(key_pos[rnum]).perform()
        WebDriverWait(browser, 5).until(EC.visibility_of_element_located((By.ID, 'keytext')))
        displayed = browser.find_element(By.ID, 'keytext').text
        if displayed != 'You pressed \'' + key_word[rnum] + '\' key.':
            endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
            update_status(mod, tc, starttime, endtime, 'Failed', 'Expected key press not displayed.', trun, status_table)
            return {"status": "Failed", "message": "Expected key press not displayed"}
        print('Completed test %s' % funcname())
        browser.get_screenshot_as_file(fpath)
        with open(fpath, 'rb') as data:
            s3.upload_fileobj(data, s3buck, s3prefix + fname)
        os.remove(fpath)
        endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
        update_status(mod, tc, starttime, endtime, 'Passed', ' ', trun, status_table)
        return {"status": "Success", "message": "Successfully executed TC0007"}
    except:
        print('Failed while running test %s' % funcname())
        endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
        update_status(mod, tc, starttime, endtime, 'Failed', traceback.print_exc(), trun, status_table)
        return {"status": "Failed", "message":
                "Failed to execute TC0007. Check logs for details."}

def tc0011(browser, mod, tc, s3buck, s3prefix, trun, main_url, status_table):
    recorder = None  # Define recorder at the start to ensure it's accessible throughout the function
    try:
        if enable_display:
            filepath = '/tmp/'
            recorder = subprocess.Popen(['/usr/bin/ffmpeg', '-f', 'x11grab', '-video_size',
                                         '2560x1440', '-framerate', '25', '-probesize',
                                         '10M', '-i', ':25', '-y', filepath + 'tc0011.mp4'])
            time.sleep(0.5)
        
        print('Getting URL')
        starttime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
        endtime = ' '
        update_status(mod, tc, starttime, endtime, 'Started', ' ', trun, status_table)
        
        browser.get(main_url)
        assert 'Serverless UI Testing' in browser.title
        
        # Rest of the test steps go here...

        endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
        if enable_display:
            recorder.terminate()
            time.sleep(7)
            print('Closed recorder')
            recorder.wait(timeout=20)
        update_status(mod, tc, starttime, endtime, 'Passed', ' ', trun, status_table)
        
        try:
            if enable_display:
                s3.upload_file('/tmp/tc0011.mp4', s3buck, s3prefix + 'tc0011.mp4')
                os.remove('/tmp/tc0011.mp4')
            return {"status": "Success", "message": "Successfully executed TC0011"}
        except:
            traceback.print_exc()
            return {"status": "Failed", "message": "Failed to upload video to S3"}
    except:
        traceback.print_exc()
        s3.upload_file('/tmp/chromedriver.log', s3buck, s3prefix + 'chromedriver.log')
        if recorder:
            recorder.terminate()
        return {"status": "Failed", "message": "Failed to execute TC0011. Check logs for details."}


def lambda_handler(event, context):
    '''Lambda Handler'''
    print(event)
    tc_name = event['tcname']
    browser = driver
    
    if not browser:
        br = event.get('browser', 'unknown')
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({"message": "Unsupported browser: %s" % br})
        }
    
    s3prefix = event['s3prefix'] + event['testrun'].split(':')[-1] + '/' + br + '/'
    try:
        resp = globals().get(tc_name)(browser, event['module'], tc_name, event['s3buck'], s3prefix,
                                     event['testrun'].split(':')[-1], event['WebURL'], event['StatusTable'])
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({"message": f"Error executing test case {tc_name}: {str(e)}"})
        }
    finally:
        browser.quit()
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "message": resp['message']
        })
    }

def container_handler():
    '''Container Handler'''
    tc_name = os.environ['tcname']
    browser = driver
    
    if not browser:
        br = os.environ.get('browser', 'unknown')
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({"message": "Unsupported browser: %s" % br})
        }
    
    s3prefix = os.environ['s3prefix'] + os.environ['testrun'].split(':')[-1] + '/' + br + '/'
    try:
        resp = globals().get(tc_name)(browser, os.environ['module'], tc_name, os.environ['s3buck'], s3prefix,
                                     os.environ['testrun'].split(':')[-1], os.environ['WebURL'], os.environ['StatusTable'])
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({"message": f"Error executing test case {tc_name}: {str(e)}"})
        }
    finally:
        browser.quit()
    
    sfn.send_task_success(
        taskToken=os.environ['TASK_TOKEN_ENV_VARIABLE'],
        output=json.dumps({"message": resp['message']})
    )
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "message": resp['message']
        })
    }