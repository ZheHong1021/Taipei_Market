#!python
from selenium import webdriver

#下拉選單的method
from selenium.webdriver.support.ui import Select # Select
from selenium.webdriver.common.by import By 

from  selenium.webdriver.support.ui  import  WebDriverWait 
from  selenium.webdriver.support  import  expected_conditions  as  EC

# 自動更新chromeDriver
import chromedriver_autoinstaller

import pymysql
import time

def connect_db(host, user, pwd, dbname, port):
    try:
        db = pymysql.connect(
            host = host,
            user = user,
            passwd = pwd,
            database = dbname,
            port =  int(port)
        )
        # print("連線成功")
        return db
    except Exception as e:
        print('連線資料庫失敗: {}'.format(str(e)))
    return None


if __name__ == "__main__":
    chromedriver_autoinstaller.install() # 安裝最適合的版本
    url = "http://www.tapmc.com.taipei/tapmc10/PD_Trend.aspx?Q=1" # 爬蟲網址

    option = webdriver.ChromeOptions()
    # 【參考】https://ithelp.ithome.com.tw/articles/10244446
    option.add_argument("headless") # 不開網頁搜尋
    option.add_argument('blink-settings=imagesEnabled=false') # 不加載圖片提高效率
    option.add_argument('--log-level=3') # 這個option可以讓你跟headless時網頁端的console.log說掰掰
    """下面參數能提升爬蟲穩定性"""
    option.add_argument('--disable-dev-shm-usage') # 使用共享內存RAM
    option.add_argument('--disable-gpu') # 規避部分chrome gpu bug

    # driver = webdriver.Chrome(chrome_options=option) #啟動模擬瀏覽器
    driver = webdriver.Chrome("./chromedriver.exe", chrome_options=option) #啟動模擬瀏覽器
    driver.get(url) # 取得網頁代碼

    conn = connect_db(
        host='127.0.0.1',
        user='root',
        pwd='Ru,6e.4vu4wj/3',
        dbname='greenhouse',
        port=3306,
    ) # 資料庫連線
    
    # print( conn )
    time.sleep(1)
    try:
        select_Category = Select( driver.find_element( By.ID, "ddl_list" ) )
        select_Category.select_by_visible_text( "蔬菜" ) # 【分類】選擇蔬菜
        radio_Month = driver.find_element( By.ID, "rblDateType_2" ) # 【日期別】選擇『月』
        radio_Month.click()

        """選擇特定日期"""
        # year = "112"
        # month = "01"
        # select_Year_S = Select( driver.find_element( By.ID, "ddl_year_s" ) ) # 起始年
        # select_Year_S.select_by_visible_text( year ) # 【起始年】選擇

        # select_Month_S = Select( driver.find_element( By.ID, "ddl_mon_s" ) ) # 起始月
        # select_Month_S.select_by_visible_text( month ) # 【起始月】選擇

        # select_Year_E = Select( driver.find_element( By.ID, "ddl_year_e" ) ) # 終點年
        # select_Year_E.select_by_visible_text( year ) # 【終點年】選擇

        # select_Month_E = Select( driver.find_element( By.ID, "ddl_mon_e" ) ) # 終點月
        # select_Month_E.select_by_visible_text( month ) # 【終點月】選擇

        radio_Crop = driver.find_element( By.ID, "rbl_class_1" ) # 【輸入產品】選擇『類別菜種』
        radio_Crop.click()

        driver.implicitly_wait(2) 

        # search_List = ["【S】根莖菜類", "【L】葉菜類", "【F】花果菜類", "水果"] # 要抓的列表(水果處理方式會比較不一樣)
        search_List = [
            {'code': "S", "name": "根莖菜類"},
            {'code': "L", "name": "葉菜類"},
            {'code': "F", "name": "花果菜類"},
            {'code': "", "name": "水果"}, # 水果處理方式會比較不一樣
        ]

        for item in search_List:
            code = item["code"]
            name = item["name"]
            print(name)
            if (name != "水果"):
                select_SearchList = Select( driver.find_element( By.ID, "list_item" ) ) # 【查詢項目】
                select_SearchList.select_by_visible_text( f"【{code}】{name}" )
                # select_SearchList.select_by_visible_text( "【S】根莖菜類" )

                btn_Add = driver.find_element( By.ID, "btn_add" ) # 加入按鈕
                btn_Add.click()
                
            
            else: # 最後這邊還需要抓水果行情價格
                select_Category = Select( driver.find_element( By.ID, "ddl_list" ) ) # 要將種類進行切換
                select_Category.select_by_visible_text( "水果" ) # 【分類】選擇蔬菜


            time.sleep(1)
            btn_Search = driver.find_element( By.ID, "btn_submit" ) # 查詢按鈕
            btn_Search.click()
            
            # 【參考教學】https://stackoverflow.com/questions/61859356/how-to-click-the-ok-button-within-an-alert-using-python-selenium
            WebDriverWait(driver, 10).until(EC.alert_is_present()) # 等待查看是否有Alert
            driver.switch_to.alert.accept() # 當Alert出現時，按接受


            date = driver.find_element( By.XPATH, '//*[@id="tbResult"]/tbody/tr[1]/td[1]' ).text # 取得文字

            price_attr = driver.find_element( By.XPATH, '//*[@id="tbResult"]/thead/tr[2]/th[6]').text
            price = driver.find_element( By.XPATH, '//*[@id="tbResult"]/tbody/tr[1]/td[6]' ).text # 取得文字

            volume_attr = driver.find_element( By.XPATH, '//*[@id="tbResult"]/thead/tr[2]/th[7]').text
            volume = driver.find_element( By.XPATH, '//*[@id="tbResult"]/tbody/tr[1]/td[7]' ).text # 取得文字

            print( f"【{date}】" ) # 【111年08月】
            print( f"{price_attr}: {price}") # 平均價(元/公斤): 38.4
            print( f"{volume_attr}: {volume}") # 交易量(公斤): 3907604
            


            cursor = conn.cursor()
            # 找尋資料庫有無資料
            sql = f"""SELECT * FROM veg_market_price WHERE `category` = '{name}' and `date_ROC` = '{date}'"""
            cursor.execute(sql)
            result = cursor.fetchone() # 找不到時會回傳 "None"

            if(result):
                with conn.cursor() as cursor: # 資料處理好後，進行資料庫新增動作
                    command = "UPDATE `veg_market_price` SET `price` = %s, `volume` = %s WHERE `category` = %s and `date_ROC` = %s;"
                    cursor.execute(command, (price, volume, name, date))
                #儲存變更
                conn.commit()
                print("......更新成功")
            
            else:
                with conn.cursor() as cursor: # 資料處理好後，進行資料庫新增動作
                    command = "INSERT INTO `veg_market_price` (`category`, `price`, `volume`, `date_ROC`) VALUES (%s, %s, %s, %s);"
                    cursor.execute(command, (name, price, volume, date))
                #儲存變更
                conn.commit()
                print("......新增成功")

            print("------------------------")
            # driver.implicitly_wait(2) # seconds

        conn.close()

    except KeyboardInterrupt :
        print("----(已中斷程式)----")
        driver.close()
        driver.quit()

    finally:
        print("----(ChromeDriver已關閉)----")
        driver.close()
        driver.quit()




