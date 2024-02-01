#region (Selenium 相關套件)
from selenium import webdriver

from selenium.webdriver.support.ui import Select #下拉選單的method
from selenium.webdriver.common.by import By 

from  selenium.webdriver.support.ui  import  WebDriverWait 
from  selenium.webdriver.support  import  expected_conditions  as  EC
#endregion


import pymysql
import time
from datetime import date, datetime

import logging

def setup_logger(log_file='app.log'):
    # 创建一个记录器
    logger = logging.getLogger('my_logger')
    logger.setLevel(logging.DEBUG)

    # 创建一个文件处理程序，用于将日志写入文件
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # 创建一个控制台处理程序，用于在控制台输出日志
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # 创建一个格式器，用于定义日志消息的格式
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 将处理程序添加到记录器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

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

def SelectMarketPrice(category, date):
    try:
        with db.cursor() as cursor:
            cursor.execute(
                """SELECT * FROM veg_market_price 
                    WHERE `category` = %s and `date_ROC` = %s
                """,
                (category, date)
            )

            row = cursor.fetchone() # 找不到時會回傳 "None"

            return row if row else None
    except Exception as e:
        print(f"執行[SelectMarketPrice]方法時發現錯誤: {e}")
        return None

def UpdateMarketPrice(price, volume, category, date):
    try:
        with db.cursor() as cursor:
            cursor.execute(
                """UPDATE `veg_market_price` SET `price` = %s, `volume` = %s 
                    WHERE `category` = %s and `date_ROC` = %s;
                """,
                (price, volume, category, date, )
            )

            db.commit()
            return True
    except Exception as e:
        print(f"執行[UpdateMarketPrice]方法時發現錯誤: {e}")
        return None
    
def InsertMarketPrice(price, volume, category, date):
    try:
        with db.cursor() as cursor:
            cursor.execute(
                """INSERT INTO `veg_market_price` 
                    (`price`, `volume`, `category`, `date_ROC`) 
                    VALUES (%s, %s, %s, %s);
                """,
                (price, volume, category, date, )
            )
            db.commit()
            return True
    except Exception as e:
        print(f"執行[InsertMarketPrice]方法時發現錯誤: {e}")
        return None
    
def Crawler(url):
    try:
        #region (chromedriver的設定)
        option = webdriver.ChromeOptions()
        # 【參考】https://ithelp.ithome.com.tw/articles/10244446
        # option.add_argument("headless") # 不開網頁搜尋
        option.add_argument('blink-settings=imagesEnabled=false') # 不加載圖片提高效率
        option.add_argument('--log-level=3') # 這個option可以讓你跟headless時網頁端的console.log說掰掰
        """下面參數能提升爬蟲穩定性"""
        option.add_argument('--disable-dev-shm-usage') # 使用共享內存RAM
        option.add_argument('--disable-gpu') # 規避部分chrome gpu bug
        #endregion

        try:
            # driver = webdriver.Chrome(chrome_options=option) #啟動模擬瀏覽器
            driver = webdriver.Chrome(CHROMEDRIVER_PATH, chrome_options=option) #啟動模擬瀏覽器
            driver.get(url) # 取得網頁代碼
        except Exception as e:
            logger.error(f"開啟ChromeDriver發生錯誤: {e}")

        if not driver.title:
            logger.error(f"📛未成功進入頁面: {e}")
            pass
        
        print(f"✅成功進入頁面...({driver.title})")

        
        driver.implicitly_wait(5) # 引性等待 => 等待頁面跑完在往下

        # 等待出現再開始
        ddl_list = WebDriverWait(driver, 10, 1).until(
            EC.presence_of_element_located(
                (By.ID, 'ddl_list')
            )
        )
        select_Category = Select( ddl_list ) # (*下拉選單處理)
        select_Category.select_by_visible_text( "蔬菜" ) # 【分類】選擇蔬菜 
        radio_Month = driver.find_element( By.ID, "rblDateType_2" ) # 【日期別】選擇『月』
        radio_Month.click()



        #region (選擇特定日期) => 捕捉近兩個月的資料
        # year = "112"
        # month = "01"
        today = datetime.now()
        end_year = today.year
        end_month = today.month
        start_year = end_year - 1 if end_month == 1 else end_year # 如果今年已經 1月則，要捕捉到去年12月的資料
        start_month = 12 if end_month == 1 else end_month - 1

        select_Year_S = Select( driver.find_element( By.ID, "ddl_year_s" ) ) # 起始年
        select_Year_S.select_by_visible_text( str(start_year - 1911) ) # 【起始年】選擇

        select_Month_S = Select( driver.find_element( By.ID, "ddl_mon_s" ) ) # 起始月
        start_month = f"0{start_month}" if start_month < 10 else str(start_month)
        select_Month_S.select_by_visible_text( start_month ) # 【起始月】選擇

        select_Year_E = Select( driver.find_element( By.ID, "ddl_year_e" ) ) # 終點年
        select_Year_E.select_by_visible_text( str(end_year - 1911) ) # 【終點年】選擇

        select_Month_E = Select( driver.find_element( By.ID, "ddl_mon_e" ) ) # 終點月
        end_month = f"0{end_month}" if end_month < 10 else str(end_month)
        select_Month_E.select_by_visible_text( end_month ) # 【終點月】選擇
        #endregion

        #region 【輸入產品】選擇『類別菜種』 (等待出現再開始)
        radio_Crop = WebDriverWait(driver, 10, 1).until(
            EC.presence_of_element_located(
                (By.ID, 'rbl_class_1')
            )
        )
        radio_Crop.click() # 點擊進行下一步查詢
        #endregion

        # time.sleep(2) # 強制等待 => 等待頁面跑完在往下


        # 【查詢項目】
        # search_List = ["【S】根莖菜類", "【L】葉菜類", "【F】花果菜類", "水果"] # 要抓的列表(水果處理方式會比較不一樣)
        search_List = [
            {'code': "S", "category": "根莖菜類"},
            {'code': "L", "category": "葉菜類"},
            {'code': "F", "category": "花果菜類"},
            {'code': "", "category": "水果"}, # 水果處理方式會比較不一樣
        ]
        
        for item in search_List:
            code = item["code"]
            category = item["category"]
            print(category)

            #region 加入作物項目
            if (category != "水果"):
                select_SearchList = WebDriverWait(driver, 10, 1).until(
                    EC.presence_of_element_located(
                        (By.ID, 'list_item')
                    )
                )
                select_SearchList = Select( select_SearchList ) # 【查詢項目】
                # select_SearchList = Select( driver.find_element( By.ID, "list_item" ) ) # 【查詢項目】
                select_SearchList.select_by_visible_text( f"【{code}】{category}" ) # 透過 text去選擇選項 => EX: 【{S}】根莖菜類
                btn_Add = driver.find_element( By.ID, "btn_add" ) # 點擊『加入按鈕』
                btn_Add.click()
            
            else: # 最後這邊還需要抓水果行情價格(不用選系向 => 直接查詢)
                select_Category = WebDriverWait(driver, 10, 1).until(
                    EC.presence_of_element_located(
                        (By.ID, 'ddl_list')
                    )
                )
                select_Category = Select( select_Category) # 要將種類進行切換
                select_Category.select_by_visible_text( "水果" ) # 【分類】選擇蔬菜
            #endregion

            #region 點擊『查詢按鈕』
            time.sleep(1.5)

            btn_Search = driver.find_element( By.ID, "btn_submit" )
            btn_Search.click()
            
            # 當跳出 alert時 => 自動按接受
            # 【參考教學】https://stackoverflow.com/questions/61859356/how-to-click-the-ok-button-within-an-alert-using-python-selenium
            WebDriverWait(driver, 10, 1).until(EC.alert_is_present()) # 等待查看是否有Alert
            driver.switch_to.alert.accept() # 當Alert出現時，按接受
            #endregion


            #region (取得需要的資料)
            date = driver.find_element( By.XPATH, '//*[@id="tbResult"]/tbody/tr[1]/td[1]' ).text # 取得文字
            price_attr = driver.find_element( By.XPATH, '//*[@id="tbResult"]/thead/tr[2]/th[6]').text
            price = driver.find_element( By.XPATH, '//*[@id="tbResult"]/tbody/tr[1]/td[6]' ).text # 取得文字
            volume_attr = driver.find_element( By.XPATH, '//*[@id="tbResult"]/thead/tr[2]/th[7]').text
            volume = driver.find_element( By.XPATH, '//*[@id="tbResult"]/tbody/tr[1]/td[7]' ).text # 取得文字

            
            print( f"【{date}】" ) # 【111年08月】
            print( f"{price_attr}: {price}") # 平均價(元/公斤): 38.4
            print( f"{volume_attr}: {volume}") # 交易量(公斤): 3907604
            #endregion

            #region (資料庫匯入)
            select_result = SelectMarketPrice(category, date)
            if select_result: # 存在 => 更新資料
                UpdateMarketPrice(
                    price=price, 
                    volume=volume, 
                    category=category,
                    date=date
                )
                print("......✅ 更新成功")
            else: # 不存在 => 新增資料
                InsertMarketPrice(
                    price=price, 
                    volume=volume, 
                    category=category,
                    date=date
                )
                print("......✅ 新增成功")
            
            print("---------------------")

            #endregion

            time.sleep(1.5) # 讓操作間隔不要太快 (小心被 Ban)

    except KeyboardInterrupt:
        print("----(已中斷程式)----")

    finally:
        print("----(ChromeDriver已關閉)----")
        driver.close()
        driver.quit()

if __name__ == "__main__":
    # 操作日誌
    logger = setup_logger()

    # chromedriver_autoinstaller.install() # 安裝最適合的版本
    CHROMEDRIVER_PATH = "./chromedriver.exe"
    url = "http://www.tapmc.com.taipei/tapmc10/PD_Trend.aspx?Q=1" # 爬蟲網址

    db = connect_db(
        host='127.0.0.1',
        user='root',
        pwd='Ru,6e.4vu4wj/3',
        dbname='greenhouse',
        port=3306,
    ) # 資料庫連線
    
    try:
        Crawler(url)
        logger.info(f"程式執行成功...")
    except Exception as e :
        logger.error(f"發生不明錯誤: {e}")

    finally:
        print("----(程式執行結束，三秒後關閉視窗)----")
        logger.info("--------------------------")
        time.sleep(3)




