
import pandas as pd
import numpy as np
import streamlit as st
import datetime
import openpyxl
from seaborn import load_dataset
from streamlit_option_menu import option_menu
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb


#''' CARGA DE TABLAS '''

# df_format = pd.read_excel('df_prueba.xlsx',sheet_name="formato")
# df_indi = pd.read_excel('df_prueba.xlsx',sheet_name="individual")



def main() :

    ######################################## ENCABEZADO #######################################

    st.set_page_config(page_title='Consumo Energético',
                           page_icon=':bulb:')
                           #layout='wide')

    st.title(':zap: CONSUMO ENERGÉTICO')

    selected = option_menu (
        menu_title = None,
        options=['Registro','Gráfico','Datos'],
        icons=['bookmark-check-fill','bar-chart-fill','cloud-download-fill'],
        orientation='horizontal',
        styles={"container": {"padding": "0!important", "background-color": "orange"},
                "icon": {"color": "yellow", "font-size": "25px"}, 
                "nav-link": {"font-size": "20px", "text-align": "center", "margin":"7px", "--hover-color": "orange"},
                "nav-link-selected": { "margin":"7px","background-color": "black", "color" : "orange"}}
        )                   
        
    st.write(" --- ") 
    #############################################           CARGA           ##########################################
    
    st.markdown('''**<th align="left"> CARGAR DATOS :</th>**''', unsafe_allow_html=True)
    
    st.markdown("*Realizar la carga el archivo **'.xlsx'** que contiene el registro histórico del consumo de energia.*")   
    
    data_file = st.file_uploader("Importar archivo ( formato : xlsx )",type=['xlsx'])

    if data_file is not None:
            # file_details = {"Filename":data_file.name,"FileType":data_file.type,"FileSize":data_file.size}
            # st.write(file_details)    
            df_format = pd.read_excel(data_file,sheet_name="formato")
            df_indi =  pd.read_excel(data_file,sheet_name="individual")

            st.write(" --- ") 
    ##########################################    CUERPO 1 - FORMATO RECIBO    ##########################################

            st.markdown('''**<th align="left"> REGISTRAR NUEVOS DATOS :</th>**''', unsafe_allow_html=True)

            
            st.markdown("*Completar las casillas con la información actual y presente en el recibo de luz.*")   

            st.markdown('''**<p align="center">DETALLE DEL CONSUMO</p>**''', unsafe_allow_html=True)
          
            column1, column2, column3 = st.columns([1,1,1],gap="small")
            with st.container():
                with column1: 
                    fecha = st.date_input("FECHA DE LECTURA :")
                    st.markdown("**Seleccionar 01 de cada mes.*")
                with column2: 
                    lectura= st.number_input('LECTURA ACTUAL : ')
                with column3: 
                    kwh = st.number_input('PRECIO DE Kwh : ')
                    var_lect= float(lectura - df_format.loc[0,'LECTURA'])

            st.markdown('''**<p align="center">DETALLE DE IMPORTES</p>**''', unsafe_allow_html=True)
            column1, column2, column3 = st.columns([1,1,1],gap="small")

            with st.container():
                with column1:        
                    repos_man = st.number_input('REPOSICIÓN Y MANTENI. : ')
                    carg_fij= st.number_input('CARGO FIJO : ')
                    carg_ener= float(kwh*var_lect)
                with column2: 
                    int_conv= st.number_input('INTERES COMPENSATORIO/CONV. : ')
                    alumb_pub= st.number_input('ALUMBRADO PUBLICO : ')
                    sub_total= float(repos_man + carg_fij + carg_ener + int_conv + alumb_pub)
                    igv= float(sub_total*0.18)
                    total_mes_actual= float(sub_total + igv)
                    aport_ley= st.number_input('APORTE DE LEY : ')                   

                with column3: 
                    descuento= st.number_input('DL 25844 U OTRO DSCT. :')                                        
                    cuot_conv= st.number_input('RECARGO MORA/CUO.CONV. :')
                    redondeo= st.number_input('REDONDEO ACTUAL :')
                    redondeo2= float(df_format.loc[0,'REDONDEO']*(-1))
                    total= round( total_mes_actual + aport_ley + descuento + cuot_conv + redondeo + redondeo2,2)

                    cuot_energ_adic= round( repos_man + carg_fij + int_conv + alumb_pub + igv + aport_ley + cuot_conv + redondeo + redondeo2,2)
                    cea_ind= round(cuot_energ_adic/3,2)

                    cor=0
                    rep=0
                    camb_prec=0
                    refac=0 

                    # ''' TABLA TEMPORAL DEL FORMATO RECIBO '''

                    df_format_temporal = pd.DataFrame(np.array([[fecha,kwh,lectura,var_lect,repos_man,carg_fij,carg_ener,int_conv,alumb_pub,sub_total,
                                                                igv,total_mes_actual,aport_ley,descuento,cuot_conv,redondeo,redondeo2,total,cuot_energ_adic,
                                                                cea_ind,cor,rep,camb_prec,refac]]),
                                                                columns=['MES', 'KWh S/.', 'LECTURA', 'VAR. LECTURA', 'REPOSICIÓN Y MANTENIM.',
                                                                        'CARGO FIJO', 'CARGO ENERGIA', 'INTERES CONVENIO', 'ALUMBRADO PUBLICO',
                                                                        'SUBTOTAL', 'IGV', 'TOTAL MES ACTUAL', 'APORTE DE LEY:','OTROS',
                                                                        'cuota de convenio', 'REDONDEO', 'REDONDEO 2', 'TOTAL A PAGAR :',
                                                                        'CONSUMO DE ENERGIA ADICIONAL', 'C.E.A. INDIVID.',
                                                                        'COR-Fus. o interr (s/r)', 'REP-Fus. o interrup(s/r)',
                                                                        'Cambio precios 2017-2020', 'I.G.V. 18% Refact.'])
                    df_format_exportar=pd.concat([df_format_temporal,df_format],ignore_index=True,sort=False)
                    new_total= round(total-df_format.loc[0,'TOTAL A PAGAR :'],2)

                    df_format_temporal_visual = pd.DataFrame(df_format_temporal.iloc[:,1:17].transpose( ) )
            
            with st.container():
                st.dataframe(df_format_temporal_visual,height=600,width=300)

            st.write(" --- ")   
    ###########################################   CUERPO 2 - CONSUMO POR INDIVIDUO   #######################################

            st.markdown('''**<p align="center">REGISTRAR LECTURA DE CADA PERSONA</p>**''', unsafe_allow_html=True)
            left_column, right_column = st.columns([1,1],gap="large")

            with st.container():
                mes= [fecha,fecha,fecha]
                item= ['ANDY','WILMER','NOEMI']

                with left_column:        
                    i_lectura= [st.number_input('LECTURA ACTUAL WILMER: '),
                                st.number_input('LECTURA ACTUAL NOEMI: ')]
                    i_lectura.insert(0,(lectura-i_lectura[0]-i_lectura[1])) 

                    i_var_lect= [float(i_lectura[0] - df_indi.loc[0,'LECTURA']), 
                                float(i_lectura[1] - df_indi.loc[1,'LECTURA']), 
                                float(i_lectura[2] - df_indi.loc[2,'LECTURA'])]
                    cons_ener= [round(i_var_lect[0]*kwh,3),
                                round(i_var_lect[1]*kwh,3),
                                round(i_var_lect[2]*kwh,3)]
                    cons_ener_ad = [round(cea_ind,2),round(cea_ind,2),round(cea_ind,2)]

                    xpagar= [round((cons_ener[0] + cons_ener_ad[0])/3,2),
                            round(cons_ener[1] + cons_ener_ad[1] +(cons_ener[0] + cons_ener_ad[0])/3,2),
                            round(cons_ener[2] + cons_ener_ad[2] +(cons_ener[0] + cons_ener_ad[0])/3,2)] 


                # ''' TABLA TEMPORAL DEL CONSUMO POR INDIVIDUO '''
                data    = list(zip(mes,item,i_lectura,i_var_lect,cons_ener,cons_ener_ad,xpagar))
                df_indi_temporal = pd.DataFrame(data,columns=['MES', 'ITEM', 'LECTURA', 'VAR. LECTURA', 'CONSUMO ENERGIA(S/.)','C.E.ADICIONAL', 'X PAGAR'])
                
                
                andy_paga   = df_indi_temporal[df_indi_temporal['ITEM']=='ANDY'].iloc[0,6]
                wilmer_paga = df_indi_temporal[df_indi_temporal['ITEM']=='WILMER'].iloc[0,6] 
                noemi_paga  = df_indi_temporal[df_indi_temporal['ITEM']=='NOEMI'].iloc[0,6]

                andy_var_pago   = float(df_indi_temporal.loc[0,'X PAGAR'] - df_indi.loc[0,'X PAGAR'])
                wilmer_var_pago = float(df_indi_temporal.loc[1,'X PAGAR'] - df_indi.loc[1,'X PAGAR'])
                noemi_var_pago  = float(df_indi_temporal.loc[2,'X PAGAR'] - df_indi.loc[2,'X PAGAR'])

                df_indi_exportar = pd.concat([df_indi_temporal,df_indi],ignore_index=True,sort=False)

                with right_column:
                    st.markdown('''**<p align="center">A PAGAR POR PERSONA</p>**''', unsafe_allow_html=True)
                    st.metric('CONSUMO DEL MES',total,new_total,delta_color="inverse")
                    # st.dataframe(df_indi_temporal[['ITEM','LECTURA','X PAGAR']].head(3),height=145,width=600)
                    # st.write("Consumo Total : ",f'S/. {total:,.2f}')
                    
                col1, col2,col3 = st.columns(3)
                col1.metric("**ANDY**", f'S/.{andy_paga:,.2f}' , f'{andy_var_pago:,.2f} Soles', help='**ROJO** *significa que se esta pagando más y* **VERDE** *que se esta pagando menos (respecto al mes anterior)*',delta_color="inverse")
                col2.metric("**WILMER**", f'S/.{wilmer_paga:,.2f}', f'{wilmer_var_pago:,.2f} Soles', help='**ROJO** *significa que se esta pagando más y* **VERDE** *que se esta pagando menos (respecto al mes anterior)*',delta_color="inverse")
                col3.metric("**NOEMI**", f'S/.{noemi_paga:,.2f}', f'{noemi_var_pago:,.2f} Soles', help='**ROJO** *significa que se esta pagando más y* **VERDE** *que se esta pagando menos (respecto al mes anterior)*',delta_color="inverse")

            st.write(" --- ")
     #################################################        DESCARGA        ##############################################

            st.markdown('''**<th align="left"> DESCARGAR REGISTRO :</th>**''', unsafe_allow_html=True)
            
            def convert_df(df1,df2):

                output = BytesIO()
                writer = pd.ExcelWriter(output, engine='xlsxwriter')
                df1.to_excel(writer,sheet_name="formato", index=False)
                df2.to_excel(writer,sheet_name="individual", index=False)
                workbook = writer.book
                worksheet = writer.sheets['formato']
                worksheet2 = writer.sheets['individual']
                format1 = workbook.add_format({'num_format': '0.00'}) 
                worksheet.set_column('A:A', None, format1)  
                worksheet2.set_column('A:A', None, format1)  
                writer.save()
                processed_data = output.getvalue()
                # writer.close()
                return processed_data

            xlsx = convert_df(df_format_exportar,df_indi_exportar)

            #### BOTON ####
            
            st.markdown("*Antes de realizar la descarga, verificar la información ingresada.*")   

            st.download_button(label='📥  Descarga de archivo',
                                    data=xlsx ,
                                    file_name= f'REG_{fecha}.xlsx')
                                    
            st.markdown("****Nota :** Conservar el archivo descargado para volver a cargarlo (en la sección de **CARGAR DATOS**) cuando se realice el próximo registro.*")   
           


            st.write(" --- ")


if __name__=='__main__':
    main()

