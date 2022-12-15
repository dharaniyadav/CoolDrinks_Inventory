import cv2
import numpy as np
import pandas as pd
import av
import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
from PIL import Image
import sqlite3
import torch
import PIL.Image

conn = sqlite3.connect('inventory_database.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS drinks (time TEXT, name TEXT, countt NUMERIC)')






def main():
        st.title("Cold Drinks Inventory Management System")
        choice=st.selectbox("Mode",["None","Staff"])

        def get_opened_image(image):
            return Image.open(image)
        
        RTC_CONFIGURATION = RTCConfiguration(
                  {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

        if choice=='Staff':
            st.title("Staff")
            date1=st.sidebar.date_input("Date")
            confidence_threshold=st.sidebar.slider("Confidence threshold",0.0,1.0)
            mode=st.sidebar.radio("View mode",['video','data','image'])

            if mode=="image":
                img_file_buffer = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
                detect=st.checkbox("Show the detected labels")
                if detect:
                    if img_file_buffer is not None: 
                        image = np.array(PIL.Image.open(img_file_buffer)) 
                        image = cv2.resize(image, (640, 640))
                        model = torch.hub.load('ultralytics/yolov5', 'custom' ,path='model.pt')
                        model.conf = confidence_threshold
                        results=model(image)
                        st.image(results.render()[0])
                        
                        df=results.pandas().xyxy[0]
                        list_of_names=[]
                        for i in range(len(df)):
                                list_of_names.append(df.loc[i, "name"])
                        new_df=pd.DataFrame(list_of_names,columns=["count"])
                        st.sidebar.table(new_df["count"].value_counts())

                        if(st.button("STORE")):
                            for i in range(len(df)):
                                    c.execute('INSERT INTO drinks (time,name,countt) VALUES (?, ?, ?)',( date1, (df.loc[i, "name"]) , 1))
                                    conn.commit()
                            st.write("UPDATED DATABASE:")
                            c.execute('SELECT name,sum(countt) FROM drinks GROUP BY name ')
                            read_list3=c.fetchall()
                            d = pd.DataFrame(read_list3,columns=["name","count"])
                            st.table(d) 


                else:
                    if img_file_buffer is not None:
                        image=get_opened_image(img_file_buffer)
                        with st.expander("Selected Image",expanded=True):
                            st.image(img_file_buffer,use_column_width=True)
            if mode=="data":
                st.header("DATA")
            

                drinkname=st.text_input("Enter drink name")
                drinkcount=st.text_input("Enter count")
                date=st.date_input("Select date")
                

                if(st.button("SUBMIT")):
                        c.execute('INSERT INTO drinks (time,name,countt) VALUES (?, ?, ?)',( date, drinkname , drinkcount))
                        conn.commit()
                
                read_list1=[]  
                c.execute('SELECT time,name,countt FROM drinks')
                read_list1=c.fetchall()
                df1= pd.DataFrame(
                    read_list1,
                    columns=["time","name","count"]
                )
                st.table(df1) 

                read_list2=[]    
                c.execute('SELECT name,sum(countt) FROM drinks GROUP BY name ')
                read_list2=c.fetchall()
                df2 = pd.DataFrame(
                    read_list2,
                    columns=["name","count"]
                )
                st.table(df2)  
                

                choice1=st.sidebar.radio("Download mode",['None','CSV','excel'])

                if choice1=="CSV":
                    st.download_button(label='download csv',data=df.to_csv() ,mime='text/csv' ,)

                elif choice1=="excel":
                    st.download_button(label='download excel',data="abc.xlsx" ,mime='text/xlsx')
            if mode=="video":
                st.title("Object detection video")
                webrtc_ctx = webrtc_streamer(
                key="WYH",
                mode=WebRtcMode.SENDRECV,
                rtc_configuration=RTC_CONFIGURATION,
                media_stream_constraints={"video": True, "audio": False},
                async_processing=True,)
                st.checkbox("Store")
                st.checkbox("Show the detected labels")
main()
            
               

         