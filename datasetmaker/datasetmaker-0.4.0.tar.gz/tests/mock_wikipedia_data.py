mock_election_tables = ["""Country,Parliamentary election,Parliamentary election,Parliamentary election,Presidential election,Presidential election,Presidential election,Fairness,Pop.(m),GDP($bn),IHDI,In power now
Country,Term,Last election,Next election,Term,Last election,Next election,Fairness,Pop.(m),GDP($bn),IHDI,In power now
Algeria,5 years,4 May 2017,May 2022,5 years,17 April 2014,4 July 2019,,37.9,207.0,no data,National Liberation Front
Angola,5 years,23 August 2017,August 2022,,,,Dominant-party system,25.8,98.8,.335,MPLA
Burkina Faso,5 years,29 November 2015,November 2020,5 years,29 November 2015,November 2020,,16.9,11.6,.261,People's Movement for Progress
Benin,5 years,28 April 2019,30 April 2023,,6 March 2016,2021,,10.3,8.3,.300,Cowry Forces
Botswana,5 years,24 October 2014,October 2019,,,,,2.0,18.0,.431,BDP
Burundi,5 years,29 June 2015,June 2020,5 years,21 July 2015,2020,,10.2,2.7,.269,CNDD-FDD
Cameroon,5 years,30 September 2013,October 2019,7 years,7 October 2018,October 2025,,20.5,25.0,.344,CPDM
Cape Verde,5 years,20 March 2016,March 2021,,2 October 2016,2021,,0.5,1.9,.519,Movement for Democracy
Central African Republic,5 years,30 December 2015,February 2021,,,,,4.6,1.5,.198,Faustin-Archange Touadéra
Chad,5 years,13 February 2011,2019,5 years,10 April 2016,2021,,12.8,13.5,.236,MPS
Comoros,5 years,25 January 2015,January 2020,5 years,21 February 2016,2021,,0.7,0.6,.268,Renewal of the Comoros
Democratic Republic of the Congo,5 years,30 December 2018,December 2023,,,,,67.5,32.7,.276,PPRD
Djibouti,5 years,23 February 2018,February 2023,5 years,8 April 2016,2021,,0.9,1.5,.308,Union for the Presidential Majority
Egypt,5 years,17 October 2015,November 2020,4 years,26 March 2018,2022,,91.5,306.0,.524,For the Love of Egypt
Equatorial Guinea,5 years,12 November 2017,November 2022,7 years,24 April 2016,2023,Dominant-party system,0.8,15.6,no data,Democratic Party
Ethiopia,5 years,24 May 2015,May 2020,6 years,25 October 2018,2024,Dominant-party system,94.1,47.5,.312,EPRDF
Gabon,5 years,6 October 2018,October 2023,7 years,27 August 2016,2023,Dominant-party system,1.7,19.3,.519,Gabonese Democratic Party
Gambia,5 years,6 April 2017,April 2022,5 years,1 December 2016,2021,,1.8,0.9,no data,Gambia Coalition 2016
Ghana,4 years,7 December 2016,7 December 2020,4 years,7 December 2016,7 December 2020,,25.9,48.1,.387,New Patriotic Party
Guinea,5 years,28 September 2013,2019,5 years,11 October 2015,2020,,11.8,6.1,.261,Rally of the Guinean People
Guinea-Bissau,4 years,10 March 2019,March 2023,5 years,,,,1.7,1.0,.254,PAIGC
Côte d'Ivoire,5 years,18 December 2016,December 2020,5 years,25 October 2015,October 2020,,20.3,31.1,.287,Rally of Houphouëtists
Kenya,4 years,8 August 2017,9 August 2022,,,,"Violence, ICC crime",44.4,55.2,.377,Jubilee Alliance
Lesotho,5 years,3 June 2017,June 2020,,,,,2.1,2.3,.320,Democratic Congress
Liberia,4 years,10 October 2017,10 October 2023,,,,,,,.251,Unity Party
Libya,4 years,25 June 2014,2019,,,,Recent civil war,6.2,79.0,no data,National Forces Alliance
Madagascar,5 years,20 December 2013,27 May 2019,,7 November 2018,,,,,.335,
Malawi,5 years,21 May 2019,May 2024,,,,,16.4,4.0,.287,Militant Socialist Movement
Mali,5 years,24 November 2013,June 2019,5 years,29 July 2018,2023,,,,no data,Rally for Mali
Mauritania,5 years,1 September 2018,September 2023,5 years,21 June 2014,2019,,,,.306,
Mauritius,5 years,10 December 2014,December 2019,,,,,,,.639,
Morocco,4 years,7 October 2016,October 2020,,,,Political suppression,32.8,107.0,.415,
Mozambique,5 years,15 October 2014,15 October 2019,,,,,23.9,15.0,.220,
Namibia,4 years,28 November 2014,November 2019,,,,,2.1,12.0,.344,
Niger,5 years,21 February 2016,February 2021,,,,,,,.200,Nigerien Party for Democracy and Socialism
Nigeria,4 years,23 February 2019,February 2023,,28 April 2015,,Violence,170.1,268.0,.276,APC
Republic of the Congo,5 years,16 July 2017,July 2022,5 years,20 March 2016,2021,,,,.368,
Rwanda,5 years,3 September 2018,September 2023,7 years,4 August 2017,2024,"Violence, fraud",12.0,8.0,.287,Patriotic Front
Sao Tome and Principe,4 years,7 October 2018,October 2022,5 years,17 July 2016,2021,,,,.358,
Senegal,5 years,30 July 2017,July 2022,,24 February 2019,,,,,.315,
Seychelles,5 years,8 September 2016,October 2021,,3 December 2015,2020[6][7],,,,no data,
Sierra Leone,5 years,7 March 2018,March 2023,,7 March 2018,,,6.1,4.0,.210,All People's Congress
Somalia,4 years,10 October 2016,October 2020,5 years,8 February 2017,2022,,14.0,5.8,no data,
South Africa,5 years[8],8 May 2019,May 2024,,,,,52.9,375.0,no data,ANC
Sudan,5 years,13 April 2015,April 2020,,,,,,,no data,National Congress
Swaziland,5 years,18 August 2018,August 2023,,,,Absolute monarchy.Parliament has very limited powers.Political parties are prohibited.,,,,(no political parties; no responsible government)
Tanzania,5 years,25 October 2015,October 2020,,,,,44.9,29.0,.346,CCM
Togo,5 years,20 December 2018,December 2023,5 years,25 April 2015,2020,,,,.305,
Tunisia,5 years,26 October 2014,6 October 2019,5 years,23 November 2014,10 November 2019,,10.9,82.0,.721,"Coalition: Nidaa Tounes,Ennahda Movement,Free Patriotic Union, Afek Tounes"
Uganda,5 years,18 February 2016,February 2021,,,,,35.8,21.0,.304,National Resist.
Zambia,5 years,11 August 2016,August 2021,,,,,14.3,20.0,.283,Patriotic Front
Zimbabwe,5 years,30 July 2018,July 2023,,,,Fraud,12.6,11.0,.284,Zanu-PF
""","""Country,Parliamentary election,Parliamentary election,Parliamentary election,Presidential election,Presidential election,Presidential election,Fairness,Pop.(m),GDP($bn),IHDI,In power now
Country,Term,Last election,Next election,Term,Last election,Next election,Fairness,Pop.(m),GDP($bn),IHDI,In power now
Antigua and Barbuda,5 years,21 March 2018,March 2023,,,,,,,no data,Antigua Labour Party
Argentina,2 years,22 October 2017,27 October 2019,4 years,25 October 2015,27 October 2019,,40.1,448.0,.653,Cambiemos
Bahamas,5 years,10 May 2017,May 2022,,,,,,,.658[9],Free National Movement
Barbados,5 years,24 May 2018,May 2023,,,,,,,no data,Barbados Labour Party
Belize,5 years[10],4 November 2015,February 2021,,,,,0.312,1.0,no data,United Democratic Party
Bolivia,5 years,12 October 2014,20 October 2019,5 years,12 October 2014,20 October 2019,,10.5,59.0,.444,Movement for Socialism
Bermuda,5 years,18 July 2017,July 2022,,,,,0.06,5.5,no data,One Bermuda Alliance
Brazil,4 years[11],7 October 2018,October 2022,4 years[11],7 October 2018,October 2022,,193.9,2476.0,.531,Social Liberal Party
Canada,4 years[12],19 October 2015,21 October 2019,,,,,35.1,1736.0,.832,Liberal Party
Cayman Islands,4 years,24 May 2017,May 2021,,,,,0.06,3.48,no data,People's Progressive Movement
Chile,4 years,19 November 2017,November 2021,4 years,19 November 2017,2021,,16.6,248.0,.664,
Colombia,4 years,11 March 2018,March 2022,4 years,27 May 2018,2022,,47.2,333.0,.519,Social Party
Costa Rica,4 years,4 February 2018,February 2022,4 years,4 February 2018,February 2022,,4.6,41.0,.606,National Liberation
Cuba,5 years,11 March 2018,2023,,,,,,,no data,Communist Party of Cuba
Dominica,5 years,8 December 2014,December 2019,,,,,,,no data,Dominica Labour Party
Dominican Republic,4 years,15 May 2016,May 2020,4 years,15 May 2016,May 2020,,9.4,98.7,.510,Dominican Liberation Party
Ecuador,4 years,19 February 2017,February 2021,4 years,19 February 2017,February 2021,,15.5,66.0,.537,PAIS Alliance
El Salvador,3 years,4 March 2018,March 2021,5 years,3 February 2019,2024,,6.1,23.0,.499,National Liberation
Falkland Islands,4 years,9 November 2017,November 2021,,,,,0.0026,0.1645,.874,Non-partisan Coalition
Grenada,5 years,13 March 2018,March 2023,,,,,,,no data,New National Party
Guatemala,4 years,16 June 2019,2023,4 years,16 June 2019,2023,,15.4,46.0,.389,Renewed Democratic Liberty
Guyana,5 years,11 May 2015,2019,,,,,,,.514,
Haiti,4 years,20 November 2016,October 2019,,20 November 2016,,,,,.273,
Honduras,4 years,26 November 2017,November 2021,4 years,26 November 2017,November 2021,,8.3,17.0,.458,National
Jamaica,5 years,25 February 2016,February 2021,,,,,,,.591,Jamaica Labour Party
Mexico,3 years,1 July 2018,July 2021,6 years,1 July 2018,2024,"Violence, Drug War",117.4,1155.0,.593,MORENA
Nicaragua,5 years,6 November 2016,November 2021,5 years,6 November 2016,2021,,6.0,7.0,.434,Sandinista
Panama,5 years,5 May 2019,May 2024,5 years,4 May 2014,2019,,3.4,30.0,.588,Democratic Change/Coal.
Paraguay,5 years,22 April 2018,April 2023,,,,,,,.505[9],Colorado
Peru,5 years,10 April 2016,April 2021,5 years,10 April 2016,2021,,30.4,180.0,.561,Gana Perú
Puerto Rico,4 years,8 November 2016,November 2020,4 years,8 November 2016,November 2020,,3.7,102.0,0.905,New Progressive Party
Saint Kitts and Nevis,5 years,16 February 2015,February 2020,,,,,,,no data,
Saint Lucia,5 years,6 June 2016,June 2021,,,,,,,no data,United Workers Party
Saint Vincent and the Grenadines,5 years,9 December 2015,December 2020,,,,,,,no data,Unity Labour Party
Suriname,5 years,25 May 2015,May 2020,,,,,,,.526,National Democratic Party
Trinidad and Tobago,5 years,7 September 2015,September 2020,,,,Very Fair[citation needed],1.3,43.4,.640,People's National Movement
United States,2 years[13],6 November 2018,November 2020,4 years[13],8 November 2016,November 2020,,316.4,14991.0,.821,Republican
Uruguay,5 years,26 October 2014,27 October 2019,5 years,26 October 2014,27 October 2019,,3.3,46.0,.662,Broad Front
Venezuela,5 years,6 December 2015,December 2020,6 years,20 May 2018,2024,Political suppression,28.9,315.0,.549,United Socialist
""","""Country,Parliamentary election,Parliamentary election,Parliamentary election,Presidential election,Presidential election,Presidential election,Fairness,Pop.(m),GDP($bn),IHDI,In power now
Country,Term,Last election,Next election,Term,Last election,Next election,Fairness,Pop.(m),GDP($bn),IHDI,In power now
Afghanistan,5 years,20 October 2018,2023,5 years,5 April 2014,28 September 2019,,,,no data,
Bahrain,4 years,22 November 2018,November 2022,,,,,,,no data,
Bangladesh,5 years,30 December 2018,December 2023,,,,,150.1,122,.374,Awami League
Bhutan,5 years,15 September 2018,September 2023,,,,,,,.430,
Burma,5 years,8 November 2015,November 2020,,,,,,,no data,National League for Democracy
Cambodia,5 years,29 July 2018,July 2023,,,,,,,.402,Cambodian People's Party
Hong Kong,4 years,4 September 2016,September 2020,,,,,7.1,243,no data,Pro-Beijing camp
India,5 years[14],11 April 2019,April 2024,5 years,17 July 2017,July 2022,,,,.392,BJP
Indonesia,5 years,17 April 2019,April 2024,5 years,17 April 2019,April 2024,Voter suppression,237.0,946,.514,PDI-P
Iran,4 years,26 February 2016,February 2020,4 years,19 May 2017,2021,,77.3,551,no data,Reformists
Iraq,4 years,12 May 2018,May 2022,,,,Civil War,31.1,150,no data,
Israel,4 years,9 April 2019,17 September 2019,,,,,8.7,300,.778[15],"Coalition: Likud, Kulanu,The Jewish Home,United Torah Judaism,Shas, Yisrael Beitenu"
Japan,4 years,22 October 2017,October 2021,,,,,126.6,5150,no data,Liberal Democratic
Jordan,4 years,20 September 2016,September 2020,,,,,,,.568,
Kazakhstan,4 years,20 March 2016,March 2020,,26 April 2015,2020,,,no data,,
Kuwait,4 years,26 November 2016,October 2020,,,,,,,no data,
Kyrgyzstan,5 years,4 October 2015,October 2020,6 years,15 October 2017,,,,,.516,
Laos,5 years,20 March 2016,March 2021,,,,,,,.409,Lao People's Revolutionary Party
Lebanon,4 years,6 May 2018,May 2022,,,,,,,.575,
Malaysia,5 years,9 May 2018,May 2023,,,,Alleged fraud,28.3,240,no data,Pakatan Harapan
Maldives,5 years,6 April 2019,April 2024,5 years,23 September 2018,2023,,,,.515,
Mongolia,4 years,29 June 2016,June 2020,4 years,26 June 2017,June 2021,,2.8,10,.568,Democrats
Nepal,5 years,26 November 2017,November 2022,5 years,13 March 2018,March 2023,,26.5,20,.304,Communist/Coal.
North Korea,5 years,10 March 2019,2024,,,,"One candidate per seat,chosen by the governing party.No democratic choice.Widespread intimidation.",,,,WPK
Oman,4 years,25 October 2015,October 2019,,,,Absolute monarchy.Elections to a Consultative Assembly only.Political parties are prohibited.,,,,(no political parties;no responsible government)
Pakistan,5 years,25 July 2018,July 2023,,,,"Violence, alleged tampering",182.5,230,.356,Pakistan Tehreek-e-Insaf
Palestinian Territory,,25 January 2006,,,9 January 2005,,,,,no data,
Philippines,3 years,13 May 2019,May 2022,6 years,9 May 2016,May 2022,"Violence, voter suppression",98.2,284,.524,Liberal
Singapore,5 years,11 September 2015,September 2020,6 years,13 September 2017,,,5.3,270,no data,PAP
South Korea,4 years,13 April 2016,April 2020,5 years,9 May 2017,2022,,50.0,1259,.758,Democratic Party of Korea
Sri Lanka,6 years,17 August 2015,August 2021,5 years,8 January 2015,January 2020,,20.2,65,.643,National Unity Government (UNP and UPFA)
Syria,4 years,13 April 2016,April 2020,7 years,3 June 2014,2021,Civil War,,,.515,
Taiwan,4 years,16 January 2016,January 2020,4 years,16 January 2016,January 2020,,23.3,473,no data,DPP
Tajikistan,5 years,1 March 2015,March 2020,7 years,6 November 2013,2020,,,,.507,
Thailand,4 years,24 March 2019,March 2023,,,,Military interference,66.7,425,.543,NCPO
East Timor,5 years,22 July 2017,July 2022,5 years,20 March 2017,,,,,.386,
Turkey,5 years,24 June 2018,June 2023,5 years,24 June 2018,2023,"Political suppression,[16] voter fraud,[17]military interference[18]",75.6,774,.542,AKP
Turkmenistan,5 years,25 March 2018,March 2023,7 years,12 February 2017,2024,,,,no data,
Uzbekistan,5 years,21 December 2014,December 2019,5 years,4 December 2016,2021,,,,.551,
Vietnam,5 years,22 May 2016,May 2021,,,,,,,.531,Communist Party of Vietnam
Yemen,6 years,27 April 2003,,,21 February 2012,,"Yemeni Crisis, Civil War",,,.310,
""","""Country,Parliamentary election,Parliamentary election,Parliamentary election,Presidential election,Presidential election,Presidential election,Fairness,Pop.(m),GDP($bn),IHDI,In power now,Status of executive party(s) in legislature
Country,Term,Last election,Next election,Term,Last election,Next election,Fairness,Pop.(m),GDP($bn),IHDI,In power now,Status of executive party(s) in legislature
Andorra,4 Years,7 April 2019,April 2023,,,,,,,,,
Armenia,5 years,2 April 2017,April 2022,5 years,2 March 2018,2025,,3.3,10.0,.649,"RPA, ARF",Majority Coalition
Austria,5 years,15 October 2017,2019,6 years,24 April 2016,2022,,8.5,418.0,.837,"ÖVP, FPÖ",Majority Coalition
Azerbaijan,5 years,21 November 2015,November 2020,5 years,11 April 2018,2025,,,,,,
Belarus,4 years,11 September 2016,September 2020,4 years,11 October 2015,2020,Disputed,,,,,
Belgium,5 years,26 May 2019,2024,,,,,11.2,514.0,.825,"MR, CD&V, Open VLD",Minority Coalition
Bosnia and Herzegovina,4 years,7 October 2018,October 2022,,,,,3.8,17.0,.650,Multiple,
Bulgaria,4 years,26 March 2017,March 2021,4 years,6 November 2016,2021,,6.9,51.0,.704,"GERB, Reformist Bloc",Minority Coalition; confidence from Patriotic Front
Croatia,4 years,11 September 2016,December 2020,5 years,28 December 2014,2020,,4.2,64.0,.683,"HDZ, HNS − LD",Minority Coalition; confidence from 16 other MPs
Cyprus,5 years,22 May 2016,May 2020,5 years,28 January 2018,2023,,1.1,23.0,.751,Democratic Rally,
Czech Republic,4 years,20 October 2017,October 2021,5 years,12 January 2018,2023,,10.5,214.0,.826,ANO 2011,ANO 2011 – Czech Social Democratic Party Minority + support of Communist Party of Bohemia and Moravia
Denmark,4 years,17 June 2019,2023,,,,,5.6,332.0,.845,TBD,
Estonia,4 years,3 March 2019,5 March 2023,,3 October 2016,,,1.3,21.0,.770,"Estonian Centre Party, SDE, IRL",Majority Coalition
Finland,4 years,14 April 2019,April 2023,6 years,28 January 2018,January 2024,,5.4,263.0,.839,"Centre Party, Finns Party, National Coalition Party",Majority Coalition
France,5 years,11 June 2017,June 2022,5 years,23 April 2017,April 2022,,65.7,2775.0,.812,Emmanuel Macron En Marche!,Majority
Georgia,4 years,8 October 2016,October 2020,,8 October 2016,,,,,,,
Germany,4 years[19],24 September 2017,August 2021,,,,,80.4,3604.0,.856,"CDU/CSU, SPD",Majority Coalition
Gibraltar,4 years,26 November 2015,November 2019,,,,,0.03,1.1059999999999999,.961,GSLP/Liberal Alliance,Majority
Greece,4 years,20 September 2015,20 October 2019,,,,,10.8,299.0,.760,"SYRIZA, ANEL",Majority Coalition
Hungary,4 years,8 April 2018,April 2022,,,,,9.9,138.0,.769,"Fidesz, KDNP",Majority Coalition
Iceland,4 years,28 October 2017,23 October 2021,4 years,25 June 2016,2020,,0.3,13.0,.848,"Progressive Party, Independence Party",Majority Coalition
Ireland,5 years[20],26 February 2016,10 April 2021,7 years[21],26 October 2018,October 2025,,4.6,221.0,.850,"Fine Gael, Independents",Minority Coalition; confidence from Fianna Fáil
Italy,5 years,4 March 2018,28 May 2023,,29 January 2015,,,60.4,2195.0,.776,"Five Star Movement, Lega Nord",Majority Coalition
Kosovo,4 years,11 June 2017,2020,,26 February 2016,,,,,,,
Latvia,4 years,26 October 2018,1 October 2022,,3 June 2015,,,2.0,28.0,.726,"Unity, ZZS, NA",Majority Coalition
Lithuania,4 years,9 October 2016,October 2020,5 years,11 May 2014,12 May 2019,,2.9,42.0,.727,Peasants,Minority Government
Luxembourg,5 years,14 October 2018,October 2023,,,,,0.537,42.0,.813,"DP, LSAP, DG",Majority Coalition
Macedonia,4 years,11 December 2016,December 2020,5 years,21 April 2019,2024,,,,,,VMRO-DPMNE and Democratic Union for Integration coalition
Malta,5 years,3 June 2017,June 2022,,,,,0.452,9.0,.778,Labour,Majority
Monaco,5 years,11 February 2018,February 2023,,,,,,,,,
Moldova,4 years,24 February 2019,2024,4 years,30 October 2016,2020,,3.6,7.0,.660,Liberal Democratic,
Montenegro,4 years,16 October 2016,October 2020,5 years,15 April 2018,2023,Dominant-party system,,,,,
Netherlands,4 years,15 March 2017,March 2021,,,,,17.1,836.0,.857,"VVD, CDA, D66, CU",Majority Coalition
Norway,4 years,11 September 2017,September 2021,,,,,5.2,483.0,.894,"Conservative, Progress, Venstre",Minority Coalition; confidence from KrF
Poland,4 years,25 October 2015,November 2019,5 years,10 May 2015,April 2020,,38.5,614.0,.774,Andrzej Duda PiS,Majority
Portugal,4 years,4 October 2015,6 October 2019,5 years,24 January 2016,January 2021,,10.3,238.0,.732,PS,"Minority; confidence from BE, PCP, PEV"
Romania,4 years[22],11 December 2016,December 2020,5 years,2 November 2014,November 2019,,20.1,187.0,.687,"PSD, ALDE","Majority coalition, although it is supported by UDMR."
Russia,5 years,18 September 2016,September 2021,6 years,18 March 2018,March 2024,Disputed,143.4,1858.0,.670[9],"Vladimir Putin, United Russia",Majority
San Marino,5 years,20 November 2016,November 2021,,,,,,,,,
Serbia,5 years,24 April 2016,April 2020,5 years,2 April 2017,2022,,7.1,53.0,.696,SNS,Majority
Slovakia,4 years,5 March 2016,March 2020,5 years,16 March 2019,2024,,5.4,91.0,.788,Direction – Social Democracy,Coalition with SNS and Most–Híd
Slovenia,4 years,3 June 2018,June 2022,5 years,22 October 2017,2022,,2.1,45.0,.840,Party of modern centre SMC/Social Democrat,
Spain,4 years[23],28 April 2019,May 2023,,,,,46.7,1478.0,.796,Spanish Socialist Workers' Party,Minority Coalition; confidence from Podemos
Sweden,4 years,9 September 2018,11 September 2022,,,,,9.6,539.0,.859,Social Democratic/Green,Minority Coalition; confidence from the Center Party and the Liberals
Switzerland,4 years,18 October 2015,20 October 2019,,,,,8.0,632.0,.849,see Swiss Federal Council,
Ukraine,5 years,26 October 2014,21 July 2019,5 years,31 March 2019,2024,"Disputed, Dominant-party system",44.8,180.0,.672,"Petro Poroshenko Bloc ""Solidarity""/People's Front",Majority coalition
United Kingdom,5 years[24],8 June 2017,May 2022,,,,,63.7,2429.0,.802,Conservative,Minority (Confidence and supply arrangement with the DUP)
European Union,5 years,23 May 2019,May 2024,,,,,507.9,17577.0,no data,,"EPP, S&D, ALDE (informal alliance in the EP)"
""","""Country,Parliamentary election,Parliamentary election,Parliamentary election,Presidential election,Presidential election,Presidential election,Fairness,Pop.(m),GDP($bn),IHDI,In power now
Country,Term,Last election,Next election,Term,Last election,Next election,Fairness,Pop.(m),GDP($bn),IHDI,In power now
Australia,3 years[25],18 May 2019,2022,,,,,24.1,1620.0,.858,Liberal/National
Cook Islands,4 years,14 June 2018,April 2022,,,,,,,,Cook Islands Party
Federated States of Micronesia,2 years,5 March 2019,March 2021,,,,,,,,
Fiji,4 years,14 November 2018,November 2022,,,,,,,,FijiFirst
Kiribati,4 years,30 December 2015,December 2019,,9 March 2016,,,,,,awaiting results
Marshall Islands,4 years,16 November 2015,November 2019,,,,,,,,
Nauru,3 years,9 July 2016,July 2019,,,,,,,,(no political parties)
New Zealand,3 years,23 September 2017,September 2020,,,,,4.3,161.0,no data,Labour/NZ First/Greens
Niue,3 years,6 May 2017,May 2020,,,,,,,,(no political parties)
Palau,4 years,1 November 2016,November 2020,4 years,1 November 2016,2020.0,,,,,
Papua New Guinea,5 years,24 June 2017,July 2022,,,,,8.1,13.0,no data,PNCP
Samoa,5 years,4 March 2016,March 2021,,,,,,,,HRPP
Solomon Islands,4 years,3 April 2019,April 2023,,,,,,,,broad coalition
Tonga,4 years,16 November 2017,November 2021,,,,,,,,(non-partisan)
Tuvalu,4 years,31 March 2015,2019,,,,,,,,(no political parties)
Vanuatu,4 years,22 January 2016,January 2020,,,,,,,,broad coalition
"""
]

mock_elections_html = """<table class="wikitable sortable jquery-tablesorter" style="font-size:90%;">

<thead><tr>
<th rowspan="2" class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">Country
</th>
<th colspan="3">Parliamentary election
</th>
<th colspan="3">Presidential election
</th>
<th rowspan="2" class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending"><a href="/wiki/Unfair_election" title="Unfair election">Fairness</a>
</th>
<th rowspan="2" class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending"><a href="/wiki/List_of_countries_by_population" class="mw-redirect" title="List of countries by population">Pop.</a><br>(m)
</th>
<th rowspan="2" class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending"><a href="/wiki/List_of_countries_by_GDP_(nominal)" title="List of countries by GDP (nominal)">GDP</a><br>($bn)
</th>
<th rowspan="2" class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending"><a href="/wiki/List_of_countries_by_inequality-adjusted_HDI" title="List of countries by inequality-adjusted HDI">IHDI</a>
</th>
<th rowspan="2" class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">In power now
</th></tr><tr>
<th class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">Term
</th>
<th class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">Last election
</th>
<th class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">Next election
</th>
<th class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">Term
</th>
<th class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">Last election
</th>
<th class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">Next election
</th></tr></thead><tbody>

<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/7/77/Flag_of_Algeria.svg/23px-Flag_of_Algeria.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/7/77/Flag_of_Algeria.svg/35px-Flag_of_Algeria.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/7/77/Flag_of_Algeria.svg/45px-Flag_of_Algeria.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Algeria
</td>
<td>5 years
</td>
<td><a href="/wiki/2017_Algerian_legislative_election" title="2017 Algerian legislative election"><span data-sort-value="000000002017-05-04-0000" style="white-space:nowrap">4 May 2017</span></a>
</td>
<td><span data-sort-value="000000002022-05-01-0000" style="white-space:nowrap">May 2022</span>
</td>
<td>5 years
</td>
<td><a href="/wiki/2014_Algerian_presidential_election" title="2014 Algerian presidential election"><span data-sort-value="000000002014-04-17-0000" style="white-space:nowrap">17 April 2014</span></a>
</td>
<td><a href="/wiki/2019_Algerian_presidential_election" class="mw-redirect" title="2019 Algerian presidential election"><span data-sort-value="000000002019-07-04-0000" style="white-space:nowrap">4 July 2019</span></a>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Algeria" title="Demographics of Algeria">37.9</a>
</td>
<td><a href="/wiki/Economy_of_Algeria" title="Economy of Algeria">207</a>
</td>
<td>no data
</td>
<td><a href="/wiki/National_Liberation_Front_(Algeria)" title="National Liberation Front (Algeria)">National Liberation Front</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/9/9d/Flag_of_Angola.svg/23px-Flag_of_Angola.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/9/9d/Flag_of_Angola.svg/35px-Flag_of_Angola.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/9/9d/Flag_of_Angola.svg/45px-Flag_of_Angola.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Angola
</td>
<td>5 years
</td>
<td><a href="/wiki/2017_Angolan_legislative_election" title="2017 Angolan legislative election"><span data-sort-value="000000002017-08-23-0000" style="white-space:nowrap">23 August 2017</span></a>
</td>
<td><span data-sort-value="000000002022-08-01-0000" style="white-space:nowrap">August 2022</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/Dominant-party_system" title="Dominant-party system">Dominant-party system</a>
</td>
<td><a href="/wiki/Demographics_of_Angola" title="Demographics of Angola">25.8</a>
</td>
<td><a href="/wiki/Economy_of_Angola" title="Economy of Angola">98.8</a>
</td>
<td>.335
</td>
<td><a href="/wiki/People%27s_Movement_for_the_Liberation_of_Angola" class="mw-redirect" title="People's Movement for the Liberation of Angola">MPLA</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/3/31/Flag_of_Burkina_Faso.svg/23px-Flag_of_Burkina_Faso.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/3/31/Flag_of_Burkina_Faso.svg/35px-Flag_of_Burkina_Faso.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/3/31/Flag_of_Burkina_Faso.svg/45px-Flag_of_Burkina_Faso.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Burkina Faso
</td>
<td>5 years
</td>
<td><a href="/wiki/2015_Burkinab%C3%A9_general_election" title="2015 Burkinabé general election"><span data-sort-value="000000002015-11-29-0000" style="white-space:nowrap">29 November 2015</span></a>
</td>
<td><span data-sort-value="000000002020-11-01-0000" style="white-space:nowrap">November 2020</span>
</td>
<td>5 years
</td>
<td><a href="/wiki/2015_Burkinab%C3%A9_general_election" title="2015 Burkinabé general election"><span data-sort-value="000000002015-11-29-0000" style="white-space:nowrap">29 November 2015</span></a>
</td>
<td><span data-sort-value="000000002020-11-01-0000" style="white-space:nowrap">November 2020</span>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Burkina_Faso" title="Demographics of Burkina Faso">16.9</a>
</td>
<td><a href="/wiki/Economy_of_Burkina_Faso" title="Economy of Burkina Faso">11.6</a>
</td>
<td>.261
</td>
<td><a href="/wiki/People%27s_Movement_for_Progress" title="People's Movement for Progress">People's Movement for Progress</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Flag_of_Benin.svg/23px-Flag_of_Benin.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Flag_of_Benin.svg/35px-Flag_of_Benin.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Flag_of_Benin.svg/45px-Flag_of_Benin.svg.png 2x" data-file-width="450" data-file-height="300">&nbsp;</span>Benin
</td>
<td>5 years
</td>
<td><a href="/wiki/2019_Beninese_parliamentary_election" title="2019 Beninese parliamentary election"><span data-sort-value="000000002019-04-28-0000" style="white-space:nowrap">28 April 2019</span></a>
</td>
<td><span data-sort-value="000000002023-04-30-0000" style="white-space:nowrap">30 April 2023</span>
</td>
<td>
</td>
<td><a href="/wiki/2016_Beninese_presidential_election" title="2016 Beninese presidential election"><span data-sort-value="000000002016-03-06-0000" style="white-space:nowrap">6 March 2016</span></a>
</td>
<td><span data-sort-value="000000002021-01-01-0000" style="white-space:nowrap">2021</span>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Benin" title="Demographics of Benin">10.3</a>
</td>
<td><a href="/wiki/Economy_of_Benin" title="Economy of Benin">8.3</a>
</td>
<td>.300
</td>
<td><a href="/wiki/Cowry_Forces_for_an_Emerging_Benin" title="Cowry Forces for an Emerging Benin">Cowry Forces</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Flag_of_Botswana.svg/23px-Flag_of_Botswana.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Flag_of_Botswana.svg/35px-Flag_of_Botswana.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Flag_of_Botswana.svg/45px-Flag_of_Botswana.svg.png 2x" data-file-width="1200" data-file-height="800">&nbsp;</span>Botswana
</td>
<td>5 years
</td>
<td><a href="/wiki/2014_Botswana_general_election" title="2014 Botswana general election"><span data-sort-value="000000002014-10-24-0000" style="white-space:nowrap">24 October 2014</span></a>
</td>
<td><a href="/wiki/2019_Botswana_general_election" title="2019 Botswana general election"><span data-sort-value="000000002019-10-01-0000" style="white-space:nowrap">October 2019</span></a>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/Demography_of_Botswana" class="mw-redirect" title="Demography of Botswana">2.0</a>
</td>
<td><a href="/wiki/Economy_of_Botswana" title="Economy of Botswana">18</a>
</td>
<td>.431
</td>
<td><a href="/wiki/Botswana_Democratic_Party" title="Botswana Democratic Party">BDP</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/5/50/Flag_of_Burundi.svg/23px-Flag_of_Burundi.svg.png" decoding="async" width="23" height="14" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/5/50/Flag_of_Burundi.svg/35px-Flag_of_Burundi.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/5/50/Flag_of_Burundi.svg/46px-Flag_of_Burundi.svg.png 2x" data-file-width="1000" data-file-height="600">&nbsp;</span>Burundi
</td>
<td>5 years
</td>
<td><a href="/wiki/2015_Burundian_legislative_election" title="2015 Burundian legislative election"><span data-sort-value="000000002015-06-29-0000" style="white-space:nowrap">29 June 2015</span></a>
</td>
<td><span data-sort-value="000000002020-06-01-0000" style="white-space:nowrap">June 2020</span>
</td>
<td>5 years
</td>
<td><a href="/wiki/2015_Burundian_presidential_election" title="2015 Burundian presidential election"><span data-sort-value="000000002015-07-21-0000" style="white-space:nowrap">21 July 2015</span></a>
</td>
<td><span data-sort-value="000000002020-01-01-0000" style="white-space:nowrap">2020</span>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Burundi" title="Demographics of Burundi">10.2</a>
</td>
<td><a href="/wiki/Economy_of_Burundi" title="Economy of Burundi">2.7</a>
</td>
<td>.269
</td>
<td><a href="/wiki/National_Council_for_the_Defense_of_Democracy_%E2%80%93_Forces_for_the_Defense_of_Democracy" title="National Council for the Defense of Democracy – Forces for the Defense of Democracy">CNDD-FDD</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Flag_of_Cameroon.svg/23px-Flag_of_Cameroon.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Flag_of_Cameroon.svg/35px-Flag_of_Cameroon.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Flag_of_Cameroon.svg/45px-Flag_of_Cameroon.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Cameroon
</td>
<td>5 years
</td>
<td><a href="/wiki/2013_Cameroonian_parliamentary_election" title="2013 Cameroonian parliamentary election"><span data-sort-value="000000002013-09-30-0000" style="white-space:nowrap">30 September 2013</span></a>
</td>
<td><a href="/wiki/2019_Cameroonian_parliamentary_election" title="2019 Cameroonian parliamentary election"><span data-sort-value="000000002019-10-01-0000" style="white-space:nowrap">October 2019</span></a>
</td>
<td>7 years
</td>
<td><a href="/wiki/2018_Cameroonian_presidential_election" title="2018 Cameroonian presidential election"><span data-sort-value="000000002018-10-07-0000" style="white-space:nowrap">7 October 2018</span></a>
</td>
<td><span data-sort-value="000000002025-10-01-0000" style="white-space:nowrap">October 2025</span>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Cameroon" title="Demographics of Cameroon">20.5</a>
</td>
<td><a href="/wiki/Economy_of_Cameroon" title="Economy of Cameroon">25</a>
</td>
<td>.344
</td>
<td><a href="/wiki/Cameroon_People%27s_Democratic_Movement" title="Cameroon People's Democratic Movement">CPDM</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/3/38/Flag_of_Cape_Verde.svg/23px-Flag_of_Cape_Verde.svg.png" decoding="async" width="23" height="14" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/3/38/Flag_of_Cape_Verde.svg/35px-Flag_of_Cape_Verde.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/3/38/Flag_of_Cape_Verde.svg/46px-Flag_of_Cape_Verde.svg.png 2x" data-file-width="510" data-file-height="300">&nbsp;</span>Cape Verde
</td>
<td>5 years
</td>
<td><a href="/wiki/2016_Cape_Verdean_parliamentary_election" title="2016 Cape Verdean parliamentary election"><span data-sort-value="000000002016-03-20-0000" style="white-space:nowrap">20 March 2016</span></a>
</td>
<td><span data-sort-value="000000002021-03-01-0000" style="white-space:nowrap">March 2021</span>
</td>
<td>
</td>
<td><a href="/wiki/2016_Cape_Verdean_presidential_election" title="2016 Cape Verdean presidential election"><span data-sort-value="000000002016-10-02-0000" style="white-space:nowrap">2 October 2016</span></a>
</td>
<td><span data-sort-value="000000002021-01-01-0000" style="white-space:nowrap">2021</span>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Cape_Verde" title="Demographics of Cape Verde">0.5</a>
</td>
<td><a href="/wiki/Economy_of_Cape_Verde" title="Economy of Cape Verde">1.9</a>
</td>
<td>.519
</td>
<td><a href="/wiki/Movement_for_Democracy_(Cape_Verde)" title="Movement for Democracy (Cape Verde)">Movement for Democracy</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Flag_of_the_Central_African_Republic.svg/23px-Flag_of_the_Central_African_Republic.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Flag_of_the_Central_African_Republic.svg/35px-Flag_of_the_Central_African_Republic.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Flag_of_the_Central_African_Republic.svg/45px-Flag_of_the_Central_African_Republic.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Central African Republic
</td>
<td>5 years
</td>
<td><a href="/wiki/Central_African_general_election,_2015%E2%80%9316" class="mw-redirect" title="Central African general election, 2015–16"><span data-sort-value="000000002015-12-30-0000" style="white-space:nowrap">30 December 2015</span></a>
</td>
<td><span data-sort-value="000000002021-02-01-0000" style="white-space:nowrap">February 2021</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Central_African_Republic" class="mw-redirect" title="Demographics of Central African Republic">4.6</a>
</td>
<td><a href="/wiki/Economy_of_Central_African_Republic" class="mw-redirect" title="Economy of Central African Republic">1.5</a>
</td>
<td>.198
</td>
<td><a href="/wiki/Faustin-Archange_Touad%C3%A9ra" title="Faustin-Archange Touadéra">Faustin-Archange Touadéra</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Flag_of_Chad.svg/23px-Flag_of_Chad.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Flag_of_Chad.svg/35px-Flag_of_Chad.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Flag_of_Chad.svg/45px-Flag_of_Chad.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Chad
</td>
<td>5 years
</td>
<td><a href="/wiki/2011_Chadian_parliamentary_election" title="2011 Chadian parliamentary election"><span data-sort-value="000000002011-02-13-0000" style="white-space:nowrap">13 February 2011</span></a>
</td>
<td><span data-sort-value="000000002019-01-01-0000" style="white-space:nowrap">2019</span>
</td>
<td>5 years
</td>
<td><a href="/wiki/2016_Chadian_presidential_election" title="2016 Chadian presidential election"><span data-sort-value="000000002016-04-10-0000" style="white-space:nowrap">10 April 2016</span></a>
</td>
<td><span data-sort-value="000000002021-01-01-0000" style="white-space:nowrap">2021</span>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Chad" title="Demographics of Chad">12.8</a>
</td>
<td><a href="/wiki/Economy_of_Chad" title="Economy of Chad">13.5</a>
</td>
<td>.236
</td>
<td><a href="/wiki/Patriotic_Salvation_Movement" title="Patriotic Salvation Movement">MPS</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/9/94/Flag_of_the_Comoros.svg/23px-Flag_of_the_Comoros.svg.png" decoding="async" width="23" height="14" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/9/94/Flag_of_the_Comoros.svg/35px-Flag_of_the_Comoros.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/9/94/Flag_of_the_Comoros.svg/46px-Flag_of_the_Comoros.svg.png 2x" data-file-width="1000" data-file-height="600">&nbsp;</span>Comoros
</td>
<td>5 years
</td>
<td><a href="/wiki/2015_Comorian_legislative_election" title="2015 Comorian legislative election"><span data-sort-value="000000002015-01-25-0000" style="white-space:nowrap">25 January 2015</span></a>
</td>
<td><span data-sort-value="000000002020-01-01-0000" style="white-space:nowrap">January 2020</span>
</td>
<td>5 years
</td>
<td><a href="/wiki/2016_Comorian_presidential_election" title="2016 Comorian presidential election"><span data-sort-value="000000002016-02-21-0000" style="white-space:nowrap">21 February 2016</span></a>
</td>
<td><span data-sort-value="000000002021-01-01-0000" style="white-space:nowrap">2021</span>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_the_Comoros" title="Demographics of the Comoros">0.7</a>
</td>
<td><a href="/wiki/Economy_of_the_Comoros" title="Economy of the Comoros">0.6</a>
</td>
<td>.268
</td>
<td><a href="/wiki/Convention_for_the_Renewal_of_the_Comoros" title="Convention for the Renewal of the Comoros">Renewal of the Comoros</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Flag_of_the_Democratic_Republic_of_the_Congo.svg/20px-Flag_of_the_Democratic_Republic_of_the_Congo.svg.png" decoding="async" width="20" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Flag_of_the_Democratic_Republic_of_the_Congo.svg/31px-Flag_of_the_Democratic_Republic_of_the_Congo.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Flag_of_the_Democratic_Republic_of_the_Congo.svg/40px-Flag_of_the_Democratic_Republic_of_the_Congo.svg.png 2x" data-file-width="800" data-file-height="600">&nbsp;</span>Democratic Republic of the Congo
</td>
<td>5 years
</td>
<td><a href="/wiki/2018_Democratic_Republic_of_the_Congo_general_election" title="2018 Democratic Republic of the Congo general election"><span data-sort-value="000000002018-12-30-0000" style="white-space:nowrap">30 December 2018</span></a>
</td>
<td><span data-sort-value="000000002023-12-01-0000" style="white-space:nowrap">December 2023</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_the_Democratic_Republic_of_the_Congo" title="Demographics of the Democratic Republic of the Congo">67.5</a>
</td>
<td><a href="/wiki/Economy_of_the_Democratic_Republic_of_the_Congo" title="Economy of the Democratic Republic of the Congo">32.7</a>
</td>
<td>.276
</td>
<td><a href="/wiki/People%27s_Party_for_Reconstruction_and_Democracy" title="People's Party for Reconstruction and Democracy">PPRD</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/3/34/Flag_of_Djibouti.svg/23px-Flag_of_Djibouti.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/3/34/Flag_of_Djibouti.svg/35px-Flag_of_Djibouti.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/3/34/Flag_of_Djibouti.svg/45px-Flag_of_Djibouti.svg.png 2x" data-file-width="600" data-file-height="400">&nbsp;</span>Djibouti
</td>
<td>5 years
</td>
<td><a href="/wiki/2018_Djiboutian_parliamentary_election" title="2018 Djiboutian parliamentary election"><span data-sort-value="000000002018-02-23-0000" style="white-space:nowrap">23 February 2018</span></a>
</td>
<td><span data-sort-value="000000002023-02-01-0000" style="white-space:nowrap">February 2023</span>
</td>
<td>5 years
</td>
<td><a href="/wiki/2016_Djiboutian_presidential_election" title="2016 Djiboutian presidential election"><span data-sort-value="000000002016-04-08-0000" style="white-space:nowrap">8 April 2016</span></a>
</td>
<td><span data-sort-value="000000002021-01-01-0000" style="white-space:nowrap">2021</span>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Djibouti" title="Demographics of Djibouti">0.9</a>
</td>
<td><a href="/wiki/Economy_of_Djibouti" title="Economy of Djibouti">1.5</a>
</td>
<td>.308
</td>
<td><a href="/wiki/Union_for_the_Presidential_Majority_(Djibouti)" title="Union for the Presidential Majority (Djibouti)">Union for the Presidential Majority</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/f/fe/Flag_of_Egypt.svg/23px-Flag_of_Egypt.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/f/fe/Flag_of_Egypt.svg/35px-Flag_of_Egypt.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/f/fe/Flag_of_Egypt.svg/45px-Flag_of_Egypt.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Egypt
</td>
<td>5 years
</td>
<td><a href="/wiki/2015_Egyptian_parliamentary_election" title="2015 Egyptian parliamentary election"><span data-sort-value="000000002015-10-17-0000" style="white-space:nowrap">17 October 2015</span></a>
</td>
<td><span data-sort-value="000000002020-11-01-0000" style="white-space:nowrap">November 2020</span>
</td>
<td>4 years
</td>
<td><a href="/wiki/2018_Egyptian_presidential_election" title="2018 Egyptian presidential election"><span data-sort-value="000000002018-03-26-0000" style="white-space:nowrap">26 March 2018</span></a>
</td>
<td><span data-sort-value="000000002022-01-01-0000" style="white-space:nowrap">2022</span>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Egypt" title="Demographics of Egypt">91.5</a>
</td>
<td><a href="/wiki/Economy_of_Egypt" title="Economy of Egypt">306</a>
</td>
<td>.524
</td>
<td><a href="/wiki/For_the_Love_of_Egypt" title="For the Love of Egypt">For the Love of Egypt</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/3/31/Flag_of_Equatorial_Guinea.svg/23px-Flag_of_Equatorial_Guinea.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/3/31/Flag_of_Equatorial_Guinea.svg/35px-Flag_of_Equatorial_Guinea.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/3/31/Flag_of_Equatorial_Guinea.svg/45px-Flag_of_Equatorial_Guinea.svg.png 2x" data-file-width="1200" data-file-height="800">&nbsp;</span>Equatorial Guinea
</td>
<td>5 years
</td>
<td><a href="/wiki/2017_Equatorial_Guinean_legislative_election" title="2017 Equatorial Guinean legislative election"><span data-sort-value="000000002017-11-12-0000" style="white-space:nowrap">12 November 2017</span></a>
</td>
<td><span data-sort-value="000000002022-11-01-0000" style="white-space:nowrap">November 2022</span>
</td>
<td>7 years
</td>
<td><a href="/wiki/2016_Equatorial_Guinean_presidential_election" title="2016 Equatorial Guinean presidential election"><span data-sort-value="000000002016-04-24-0000" style="white-space:nowrap">24 April 2016</span></a>
</td>
<td><span data-sort-value="000000002023-01-01-0000" style="white-space:nowrap">2023</span>
</td>
<td><a href="/wiki/Dominant-party_system" title="Dominant-party system">Dominant-party system</a>
</td>
<td><a href="/wiki/Demographics_of_Equatorial_Guinea" title="Demographics of Equatorial Guinea">0.8</a>
</td>
<td><a href="/wiki/Economy_of_Equatorial_Guinea" title="Economy of Equatorial Guinea">15.6</a>
</td>
<td>no data
</td>
<td><a href="/wiki/Democratic_Party_of_Equatorial_Guinea" title="Democratic Party of Equatorial Guinea">Democratic Party</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/7/71/Flag_of_Ethiopia.svg/23px-Flag_of_Ethiopia.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/7/71/Flag_of_Ethiopia.svg/35px-Flag_of_Ethiopia.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/7/71/Flag_of_Ethiopia.svg/46px-Flag_of_Ethiopia.svg.png 2x" data-file-width="1000" data-file-height="500">&nbsp;</span>Ethiopia
</td>
<td>5 years
</td>
<td><a href="/wiki/2015_Ethiopian_general_election" title="2015 Ethiopian general election"><span data-sort-value="000000002015-05-24-0000" style="white-space:nowrap">24 May 2015</span></a>
</td>
<td><span data-sort-value="000000002020-05-01-0000" style="white-space:nowrap">May 2020</span>
</td>
<td>6 years
</td>
<td><a href="/wiki/2018_Ethiopian_presidential_election" title="2018 Ethiopian presidential election"><span data-sort-value="000000002018-10-25-0000" style="white-space:nowrap">25 October 2018</span></a>
</td>
<td><span data-sort-value="000000002024-01-01-0000" style="white-space:nowrap">2024</span>
</td>
<td><a href="/wiki/Dominant-party_system" title="Dominant-party system">Dominant-party system</a>
</td>
<td><a href="/wiki/Demographics_of_Ethiopia" title="Demographics of Ethiopia">94.1</a>
</td>
<td><a href="/wiki/Economy_of_Ethiopia" title="Economy of Ethiopia">47.5</a>
</td>
<td>.312
</td>
<td><a href="/wiki/Ethiopian_People%27s_Revolutionary_Democratic_Front" title="Ethiopian People's Revolutionary Democratic Front">EPRDF</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/0/04/Flag_of_Gabon.svg/20px-Flag_of_Gabon.svg.png" decoding="async" width="20" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/0/04/Flag_of_Gabon.svg/31px-Flag_of_Gabon.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/0/04/Flag_of_Gabon.svg/40px-Flag_of_Gabon.svg.png 2x" data-file-width="400" data-file-height="300">&nbsp;</span>Gabon
</td>
<td>5 years
</td>
<td><a href="/wiki/2018_Gabonese_legislative_election" title="2018 Gabonese legislative election"><span data-sort-value="000000002018-10-06-0000" style="white-space:nowrap">6 October 2018</span></a>
</td>
<td><span data-sort-value="000000002023-10-01-0000" style="white-space:nowrap">October 2023</span>
</td>
<td>7 years
</td>
<td><a href="/wiki/2016_Gabonese_presidential_election" title="2016 Gabonese presidential election"><span data-sort-value="000000002016-08-27-0000" style="white-space:nowrap">27 August 2016</span></a>
</td>
<td><span data-sort-value="000000002023-01-01-0000" style="white-space:nowrap">2023</span>
</td>
<td><a href="/wiki/Dominant-party_system" title="Dominant-party system">Dominant-party system</a>
</td>
<td><a href="/wiki/Demographics_of_Gabon" title="Demographics of Gabon">1.7</a>
</td>
<td><a href="/wiki/Economy_of_Gabon" title="Economy of Gabon">19.3</a>
</td>
<td>.519
</td>
<td><a href="/wiki/Gabonese_Democratic_Party" title="Gabonese Democratic Party">Gabonese Democratic Party</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/7/77/Flag_of_The_Gambia.svg/23px-Flag_of_The_Gambia.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/7/77/Flag_of_The_Gambia.svg/35px-Flag_of_The_Gambia.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/7/77/Flag_of_The_Gambia.svg/45px-Flag_of_The_Gambia.svg.png 2x" data-file-width="600" data-file-height="400">&nbsp;</span>Gambia
</td>
<td>5 years
</td>
<td><a href="/wiki/2017_Gambian_parliamentary_election" title="2017 Gambian parliamentary election"><span data-sort-value="000000002017-04-06-0000" style="white-space:nowrap">6 April 2017</span></a>
</td>
<td><span data-sort-value="000000002022-04-01-0000" style="white-space:nowrap">April 2022</span>
</td>
<td>5 years
</td>
<td><a href="/wiki/2016_Gambian_presidential_election" title="2016 Gambian presidential election"><span data-sort-value="000000002016-12-01-0000" style="white-space:nowrap">1 December 2016</span></a>
</td>
<td><span data-sort-value="000000002021-01-01-0000" style="white-space:nowrap">2021</span>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Gambia" class="mw-redirect" title="Demographics of Gambia">1.8</a>
</td>
<td><a href="/wiki/Economy_of_Gambia" class="mw-redirect" title="Economy of Gambia">0.9</a>
</td>
<td>no data
</td>
<td><a href="/wiki/Coalition_2016" title="Coalition 2016">Gambia Coalition 2016</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/1/19/Flag_of_Ghana.svg/23px-Flag_of_Ghana.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/1/19/Flag_of_Ghana.svg/35px-Flag_of_Ghana.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/1/19/Flag_of_Ghana.svg/45px-Flag_of_Ghana.svg.png 2x" data-file-width="450" data-file-height="300">&nbsp;</span>Ghana
</td>
<td>4 years
</td>
<td><a href="/wiki/2016_Ghanaian_general_election" title="2016 Ghanaian general election"><span data-sort-value="000000002016-12-07-0000" style="white-space:nowrap">7 December 2016</span></a>
</td>
<td><span data-sort-value="000000002020-12-07-0000" style="white-space:nowrap">7 December 2020</span>
</td>
<td>4 years
</td>
<td><a href="/wiki/2016_Ghanaian_general_election" title="2016 Ghanaian general election"><span data-sort-value="000000002016-12-07-0000" style="white-space:nowrap">7 December 2016</span></a>
</td>
<td><span data-sort-value="000000002020-12-07-0000" style="white-space:nowrap">7 December 2020</span>
</td>
<td>
</td>
<td><a href="/wiki/Demography_of_Ghana" class="mw-redirect" title="Demography of Ghana">25.9</a>
</td>
<td><a href="/wiki/Economy_of_Ghana" title="Economy of Ghana">48.1</a>
</td>
<td>.387
</td>
<td><a href="/wiki/New_Patriotic_Party" title="New Patriotic Party">New Patriotic Party</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/e/ed/Flag_of_Guinea.svg/23px-Flag_of_Guinea.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/e/ed/Flag_of_Guinea.svg/35px-Flag_of_Guinea.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/e/ed/Flag_of_Guinea.svg/45px-Flag_of_Guinea.svg.png 2x" data-file-width="450" data-file-height="300">&nbsp;</span>Guinea
</td>
<td>5 years
</td>
<td><a href="/wiki/2013_Guinean_legislative_election" title="2013 Guinean legislative election"><span data-sort-value="000000002013-09-28-0000" style="white-space:nowrap">28 September 2013</span></a>
</td>
<td><a href="/wiki/2019_Guinean_legislative_election" title="2019 Guinean legislative election"><span data-sort-value="000000002019-01-01-0000" style="white-space:nowrap">2019</span></a>
</td>
<td>5 years
</td>
<td><a href="/wiki/2015_Guinean_presidential_election" title="2015 Guinean presidential election"><span data-sort-value="000000002015-10-11-0000" style="white-space:nowrap">11 October 2015</span></a>
</td>
<td><span data-sort-value="000000002020-01-01-0000" style="white-space:nowrap">2020</span>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Guinea" title="Demographics of Guinea">11.8</a>
</td>
<td><a href="/wiki/Economy_of_Guinea" title="Economy of Guinea">6.1</a>
</td>
<td>.261
</td>
<td><a href="/wiki/Rally_of_the_Guinean_People" class="mw-redirect" title="Rally of the Guinean People">Rally of the Guinean People</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/0/01/Flag_of_Guinea-Bissau.svg/23px-Flag_of_Guinea-Bissau.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/0/01/Flag_of_Guinea-Bissau.svg/35px-Flag_of_Guinea-Bissau.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/0/01/Flag_of_Guinea-Bissau.svg/46px-Flag_of_Guinea-Bissau.svg.png 2x" data-file-width="1200" data-file-height="600">&nbsp;</span>Guinea-Bissau
</td>
<td>4 years
</td>
<td><a href="/wiki/2019_Guinea-Bissau_legislative_election" title="2019 Guinea-Bissau legislative election"><span data-sort-value="000000002019-03-10-0000" style="white-space:nowrap">10 March 2019</span></a>
</td>
<td><span data-sort-value="000000002023-03-01-0000" style="white-space:nowrap">March 2023</span>
</td>
<td>5 years
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Guinea-Bissau" title="Demographics of Guinea-Bissau">1.7</a>
</td>
<td><a href="/wiki/Economy_of_Guinea-Bissau" title="Economy of Guinea-Bissau">1.0</a>
</td>
<td>.254
</td>
<td><a href="/wiki/African_Party_for_the_Independence_of_Guinea_and_Cape_Verde" title="African Party for the Independence of Guinea and Cape Verde">PAIGC</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/f/fe/Flag_of_C%C3%B4te_d%27Ivoire.svg/23px-Flag_of_C%C3%B4te_d%27Ivoire.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/f/fe/Flag_of_C%C3%B4te_d%27Ivoire.svg/35px-Flag_of_C%C3%B4te_d%27Ivoire.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/f/fe/Flag_of_C%C3%B4te_d%27Ivoire.svg/45px-Flag_of_C%C3%B4te_d%27Ivoire.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Côte d'Ivoire
</td>
<td>5 years
</td>
<td><a href="/wiki/2016_Ivorian_parliamentary_election" title="2016 Ivorian parliamentary election"><span data-sort-value="000000002016-12-18-0000" style="white-space:nowrap">18 December 2016</span></a>
</td>
<td><span data-sort-value="000000002020-12-01-0000" style="white-space:nowrap">December 2020</span>
</td>
<td>5 years
</td>
<td><a href="/wiki/2015_Ivorian_presidential_election" title="2015 Ivorian presidential election"><span data-sort-value="000000002015-10-25-0000" style="white-space:nowrap">25 October 2015</span></a>
</td>
<td><a href="/wiki/2020_Ivorian_presidential_election" class="mw-redirect" title="2020 Ivorian presidential election"><span data-sort-value="000000002020-10-01-0000" style="white-space:nowrap">October 2020</span></a>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Ivory_Coast" title="Demographics of Ivory Coast">20.3</a>
</td>
<td><a href="/wiki/Economy_of_Ivory_Coast" title="Economy of Ivory Coast">31.1</a>
</td>
<td>.287
</td>
<td><a href="/wiki/Rally_of_Houphou%C3%ABtists_for_Democracy_and_Peace" title="Rally of Houphouëtists for Democracy and Peace">Rally of Houphouëtists</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/4/49/Flag_of_Kenya.svg/23px-Flag_of_Kenya.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/4/49/Flag_of_Kenya.svg/35px-Flag_of_Kenya.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/4/49/Flag_of_Kenya.svg/45px-Flag_of_Kenya.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Kenya
</td>
<td>4 years
</td>
<td><a href="/wiki/2017_Kenyan_general_election" title="2017 Kenyan general election"><span data-sort-value="000000002017-08-08-0000" style="white-space:nowrap">8 August 2017</span></a>
</td>
<td><span data-sort-value="000000002022-08-09-0000" style="white-space:nowrap">9 August 2022</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/2007%E2%80%9308_Kenyan_crisis" title="2007–08 Kenyan crisis">Violence</a>, <a href="/wiki/International_Criminal_Court_investigation_in_Kenya" title="International Criminal Court investigation in Kenya">ICC crime</a>
</td>
<td><a href="/wiki/Demographics_of_Kenya" title="Demographics of Kenya">44.4</a>
</td>
<td><a href="/wiki/Economy_of_Kenya" title="Economy of Kenya">55.2</a>
</td>
<td>.377
</td>
<td><a href="/wiki/Jubilee_Alliance" title="Jubilee Alliance">Jubilee Alliance</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Flag_of_Lesotho.svg/23px-Flag_of_Lesotho.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Flag_of_Lesotho.svg/35px-Flag_of_Lesotho.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Flag_of_Lesotho.svg/45px-Flag_of_Lesotho.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Lesotho
</td>
<td>5 years
</td>
<td><a href="/wiki/2017_Lesotho_general_election" title="2017 Lesotho general election"><span data-sort-value="000000002017-06-03-0000" style="white-space:nowrap">3 June 2017</span></a>
</td>
<td><span data-sort-value="000000002020-06-01-0000" style="white-space:nowrap">June 2020</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Lesotho" title="Demographics of Lesotho">2.1</a>
</td>
<td><a href="/wiki/Economy_of_Lesotho" title="Economy of Lesotho">2.3</a>
</td>
<td>.320
</td>
<td><a href="/wiki/Democratic_Congress" title="Democratic Congress">Democratic Congress</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/b/b8/Flag_of_Liberia.svg/23px-Flag_of_Liberia.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/b/b8/Flag_of_Liberia.svg/35px-Flag_of_Liberia.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/b/b8/Flag_of_Liberia.svg/46px-Flag_of_Liberia.svg.png 2x" data-file-width="1140" data-file-height="600">&nbsp;</span>Liberia
</td>
<td>4 years
</td>
<td><a href="/wiki/2017_Liberian_general_election" title="2017 Liberian general election"><span data-sort-value="000000002017-10-10-0000" style="white-space:nowrap">10 October 2017</span></a>
</td>
<td><span data-sort-value="000000002023-10-10-0000" style="white-space:nowrap">10 October 2023</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>.251
</td>
<td><a href="/wiki/Unity_Party_(Liberia)" title="Unity Party (Liberia)">Unity Party</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/0/05/Flag_of_Libya.svg/23px-Flag_of_Libya.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/0/05/Flag_of_Libya.svg/35px-Flag_of_Libya.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/0/05/Flag_of_Libya.svg/46px-Flag_of_Libya.svg.png 2x" data-file-width="960" data-file-height="480">&nbsp;</span>Libya
</td>
<td>4 years
</td>
<td><a href="/w/index.php?title=2014_Libyan_House_of_Representatives_election&amp;action=edit&amp;redlink=1" class="new" title="2014 Libyan House of Representatives election (page does not exist)"><span data-sort-value="000000002014-06-25-0000" style="white-space:nowrap">25 June 2014</span></a>
</td>
<td><a href="/wiki/Next_Libyan_parliamentary_election" class="mw-redirect" title="Next Libyan parliamentary election"><span data-sort-value="000000002019-01-01-0000" style="white-space:nowrap">2019</span></a>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/2011_Libyan_Civil_War" class="mw-redirect" title="2011 Libyan Civil War">Recent civil war</a>
</td>
<td><a href="/wiki/Demographics_of_Libya" title="Demographics of Libya">6.2</a>
</td>
<td><a href="/wiki/Economy_of_Libya" title="Economy of Libya">79</a>
</td>
<td>no data
</td>
<td><a href="/wiki/National_Forces_Alliance" title="National Forces Alliance">National Forces Alliance</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Flag_of_Madagascar.svg/23px-Flag_of_Madagascar.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Flag_of_Madagascar.svg/35px-Flag_of_Madagascar.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Flag_of_Madagascar.svg/45px-Flag_of_Madagascar.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Madagascar
</td>
<td>5 years
</td>
<td><a href="/wiki/2013_Malagasy_general_election" title="2013 Malagasy general election"><span data-sort-value="000000002013-12-20-0000" style="white-space:nowrap">20 December 2013</span></a>
</td>
<td><a href="/wiki/2019_Malagasy_parliamentary_election" title="2019 Malagasy parliamentary election"><span data-sort-value="000000002019-05-27-0000" style="white-space:nowrap">27 May 2019</span></a>
</td>
<td>
</td>
<td><a href="/wiki/2018_Malagasy_presidential_election" title="2018 Malagasy presidential election"><span data-sort-value="000000002018-11-07-0000" style="white-space:nowrap">7 November 2018</span></a>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>.335
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/d/d1/Flag_of_Malawi.svg/23px-Flag_of_Malawi.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/d/d1/Flag_of_Malawi.svg/35px-Flag_of_Malawi.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/d/d1/Flag_of_Malawi.svg/45px-Flag_of_Malawi.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Malawi
</td>
<td>5 years
</td>
<td><a href="/wiki/2019_Malawian_general_election" title="2019 Malawian general election"><span data-sort-value="000000002019-05-21-0000" style="white-space:nowrap">21 May 2019</span></a>
</td>
<td><span data-sort-value="000000002024-05-01-0000" style="white-space:nowrap">May 2024</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Malawi" title="Demographics of Malawi">16.4</a>
</td>
<td><a href="/wiki/Economy_of_Malawi" title="Economy of Malawi">4</a>
</td>
<td>.287
</td>
<td><a href="/wiki/Militant_Socialist_Movement" title="Militant Socialist Movement">Militant Socialist Movement</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/9/92/Flag_of_Mali.svg/23px-Flag_of_Mali.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/9/92/Flag_of_Mali.svg/35px-Flag_of_Mali.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/9/92/Flag_of_Mali.svg/45px-Flag_of_Mali.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Mali
</td>
<td>5 years
</td>
<td><a href="/wiki/2013_Malian_parliamentary_election" title="2013 Malian parliamentary election"><span data-sort-value="000000002013-11-24-0000" style="white-space:nowrap">24 November 2013</span></a>
</td>
<td><a href="/wiki/2019_Malian_parliamentary_election" title="2019 Malian parliamentary election"><span data-sort-value="000000002019-06-01-0000" style="white-space:nowrap">June 2019</span></a>
</td>
<td>5 years
</td>
<td><a href="/wiki/2018_Malian_presidential_election" title="2018 Malian presidential election"><span data-sort-value="000000002018-07-29-0000" style="white-space:nowrap">29 July 2018</span></a>
</td>
<td>2023
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>no data
</td>
<td><a href="/wiki/Rally_for_Mali" title="Rally for Mali">Rally for Mali</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/4/43/Flag_of_Mauritania.svg/23px-Flag_of_Mauritania.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/4/43/Flag_of_Mauritania.svg/35px-Flag_of_Mauritania.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/4/43/Flag_of_Mauritania.svg/45px-Flag_of_Mauritania.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Mauritania
</td>
<td>5 years
</td>
<td><a href="/wiki/2018_Mauritanian_parliamentary_election" title="2018 Mauritanian parliamentary election"><span data-sort-value="000000002018-09-01-0000" style="white-space:nowrap">1 September 2018</span></a>
</td>
<td><span data-sort-value="000000002023-09-01-0000" style="white-space:nowrap">September 2023</span>
</td>
<td>5 years
</td>
<td><a href="/wiki/2014_Mauritanian_presidential_election" title="2014 Mauritanian presidential election"><span data-sort-value="000000002014-06-21-0000" style="white-space:nowrap">21 June 2014</span></a>
</td>
<td><span data-sort-value="000000002019-01-01-0000" style="white-space:nowrap">2019</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>.306
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/7/77/Flag_of_Mauritius.svg/23px-Flag_of_Mauritius.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/7/77/Flag_of_Mauritius.svg/35px-Flag_of_Mauritius.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/7/77/Flag_of_Mauritius.svg/45px-Flag_of_Mauritius.svg.png 2x" data-file-width="450" data-file-height="300">&nbsp;</span>Mauritius
</td>
<td>5 years
</td>
<td><a href="/wiki/2014_Mauritian_general_election" title="2014 Mauritian general election"><span data-sort-value="000000002014-12-10-0000" style="white-space:nowrap">10 December 2014</span></a>
</td>
<td><span data-sort-value="000000002019-12-01-0000" style="white-space:nowrap">December 2019</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>.639
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Flag_of_Morocco.svg/23px-Flag_of_Morocco.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Flag_of_Morocco.svg/35px-Flag_of_Morocco.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Flag_of_Morocco.svg/45px-Flag_of_Morocco.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Morocco
</td>
<td>4 years
</td>
<td><a href="/wiki/2016_Moroccan_general_election" title="2016 Moroccan general election"><span data-sort-value="000000002016-10-07-0000" style="white-space:nowrap">7 October 2016</span></a>
</td>
<td><span data-sort-value="000000002020-10-01-0000" style="white-space:nowrap">October 2020</span>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>Political suppression
</td>
<td><a href="/wiki/Demographics_of_Morocco" title="Demographics of Morocco">32.8</a>
</td>
<td><a href="/wiki/Economy_of_Morocco" title="Economy of Morocco">107</a>
</td>
<td>.415
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Flag_of_Mozambique.svg/23px-Flag_of_Mozambique.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Flag_of_Mozambique.svg/35px-Flag_of_Mozambique.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Flag_of_Mozambique.svg/45px-Flag_of_Mozambique.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Mozambique
</td>
<td>5 years
</td>
<td><a href="/wiki/2014_Mozambican_general_election" title="2014 Mozambican general election"><span data-sort-value="000000002014-10-15-0000" style="white-space:nowrap">15 October 2014</span></a>
</td>
<td><a href="/wiki/2019_Mozambican_general_election" title="2019 Mozambican general election"><span data-sort-value="000000002019-10-15-0000" style="white-space:nowrap">15 October 2019</span></a>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/Demography_of_Mozambique" class="mw-redirect" title="Demography of Mozambique">23.9</a>
</td>
<td><a href="/wiki/Economy_of_Mozambique" title="Economy of Mozambique">15</a>
</td>
<td>.220
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/0/00/Flag_of_Namibia.svg/23px-Flag_of_Namibia.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/0/00/Flag_of_Namibia.svg/35px-Flag_of_Namibia.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/0/00/Flag_of_Namibia.svg/45px-Flag_of_Namibia.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Namibia
</td>
<td>4 years
</td>
<td><a href="/wiki/2014_Namibian_general_election" title="2014 Namibian general election"><span data-sort-value="000000002014-11-28-0000" style="white-space:nowrap">28 November 2014</span></a>
</td>
<td><a href="/wiki/2019_Namibian_general_election" title="2019 Namibian general election"><span data-sort-value="000000002019-11-01-0000" style="white-space:nowrap">November 2019</span></a>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/Demography_of_Namibia" class="mw-redirect" title="Demography of Namibia">2.1</a>
</td>
<td><a href="/wiki/Economy_of_Namibia" title="Economy of Namibia">12</a>
</td>
<td>.344
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/f/f4/Flag_of_Niger.svg/18px-Flag_of_Niger.svg.png" decoding="async" width="18" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/f/f4/Flag_of_Niger.svg/27px-Flag_of_Niger.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/f/f4/Flag_of_Niger.svg/35px-Flag_of_Niger.svg.png 2x" data-file-width="700" data-file-height="600">&nbsp;</span>Niger
</td>
<td>5 years
</td>
<td><a href="/wiki/2016_Nigerien_general_election" title="2016 Nigerien general election"><span data-sort-value="000000002016-02-21-0000" style="white-space:nowrap">21 February 2016</span></a>
</td>
<td><span data-sort-value="000000002021-02-01-0000" style="white-space:nowrap">February 2021</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>.200
</td>
<td><a href="/wiki/Nigerien_Party_for_Democracy_and_Socialism" title="Nigerien Party for Democracy and Socialism">Nigerien Party for Democracy and Socialism</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/7/79/Flag_of_Nigeria.svg/23px-Flag_of_Nigeria.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/7/79/Flag_of_Nigeria.svg/35px-Flag_of_Nigeria.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/7/79/Flag_of_Nigeria.svg/46px-Flag_of_Nigeria.svg.png 2x" data-file-width="1000" data-file-height="500">&nbsp;</span>Nigeria
</td>
<td>4 years
</td>
<td><a href="/wiki/2019_Nigerian_general_election" title="2019 Nigerian general election"><span data-sort-value="000000002019-02-23-0000" style="white-space:nowrap">23 February 2019</span></a>
</td>
<td><a href="/w/index.php?title=2023_Nigerian_general_election&amp;action=edit&amp;redlink=1" class="new" title="2023 Nigerian general election (page does not exist)"><span data-sort-value="000000002023-02-01-0000" style="white-space:nowrap">February 2023</span></a>
</td>
<td>
</td>
<td><a href="/wiki/2015_Nigerian_presidential_election" class="mw-redirect" title="2015 Nigerian presidential election"><span data-sort-value="000000002015-04-28-0000" style="white-space:nowrap">28 April 2015</span></a>
</td>
<td>
</td>
<td>Violence
</td>
<td><a href="/wiki/Demographics_of_Nigeria" title="Demographics of Nigeria">170.1</a>
</td>
<td><a href="/wiki/Economy_of_Nigeria" title="Economy of Nigeria">268</a>
</td>
<td>.276
</td>
<td><a href="/wiki/All_Progressive_Congress_(Nigeria)" class="mw-redirect" title="All Progressive Congress (Nigeria)">APC</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/9/92/Flag_of_the_Republic_of_the_Congo.svg/23px-Flag_of_the_Republic_of_the_Congo.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/9/92/Flag_of_the_Republic_of_the_Congo.svg/35px-Flag_of_the_Republic_of_the_Congo.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/9/92/Flag_of_the_Republic_of_the_Congo.svg/45px-Flag_of_the_Republic_of_the_Congo.svg.png 2x" data-file-width="600" data-file-height="400">&nbsp;</span>Republic of the Congo
</td>
<td>5 years
</td>
<td><a href="/wiki/2017_Republic_of_the_Congo_parliamentary_election" title="2017 Republic of the Congo parliamentary election"><span data-sort-value="000000002017-07-16-0000" style="white-space:nowrap">16 July 2017</span></a>
</td>
<td><span data-sort-value="000000002022-07-01-0000" style="white-space:nowrap">July 2022</span>
</td>
<td>5 years
</td>
<td><a href="/wiki/2016_Republic_of_the_Congo_presidential_election" title="2016 Republic of the Congo presidential election"><span data-sort-value="000000002016-03-20-0000" style="white-space:nowrap">20 March 2016</span></a>
</td>
<td><span data-sort-value="000000002021-01-01-0000" style="white-space:nowrap">2021</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>.368
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/1/17/Flag_of_Rwanda.svg/23px-Flag_of_Rwanda.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/1/17/Flag_of_Rwanda.svg/35px-Flag_of_Rwanda.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/1/17/Flag_of_Rwanda.svg/45px-Flag_of_Rwanda.svg.png 2x" data-file-width="1080" data-file-height="720">&nbsp;</span>Rwanda
</td>
<td>5 years
</td>
<td><a href="/wiki/2018_Rwandan_parliamentary_election" title="2018 Rwandan parliamentary election"><span data-sort-value="000000002018-09-03-0000" style="white-space:nowrap">3 September 2018</span></a>
</td>
<td><span data-sort-value="000000002023-09-01-0000" style="white-space:nowrap">September 2023</span>
</td>
<td>7 years
</td>
<td><a href="/wiki/2017_Rwandan_presidential_election" title="2017 Rwandan presidential election"><span data-sort-value="000000002017-08-04-0000" style="white-space:nowrap">4 August 2017</span></a>
</td>
<td><span data-sort-value="000000002024-01-01-0000" style="white-space:nowrap">2024</span>
</td>
<td>Violence, fraud
</td>
<td><a href="/wiki/Demographics_of_Rwanda" title="Demographics of Rwanda">12.0</a>
</td>
<td><a href="/wiki/Economy_of_Rwanda" title="Economy of Rwanda">8</a>
</td>
<td>.287
</td>
<td><a href="/wiki/Rwandan_Patriotic_Front" title="Rwandan Patriotic Front">Patriotic Front</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Flag_of_Sao_Tome_and_Principe.svg/23px-Flag_of_Sao_Tome_and_Principe.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Flag_of_Sao_Tome_and_Principe.svg/35px-Flag_of_Sao_Tome_and_Principe.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Flag_of_Sao_Tome_and_Principe.svg/46px-Flag_of_Sao_Tome_and_Principe.svg.png 2x" data-file-width="2800" data-file-height="1400">&nbsp;</span>Sao Tome and Principe
</td>
<td>4 years
</td>
<td><a href="/wiki/2018_S%C3%A3o_Tom%C3%A9an_legislative_election" title="2018 São Toméan legislative election"><span data-sort-value="000000002018-10-07-0000" style="white-space:nowrap">7 October 2018</span></a>
</td>
<td><span data-sort-value="000000002022-10-01-0000" style="white-space:nowrap">October 2022</span>
</td>
<td>5 years
</td>
<td><a href="/wiki/2016_S%C3%A3o_Tom%C3%A9an_presidential_election" title="2016 São Toméan presidential election"><span data-sort-value="000000002016-07-17-0000" style="white-space:nowrap">17 July 2016</span></a>
</td>
<td><span data-sort-value="000000002021-01-01-0000" style="white-space:nowrap">2021</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>.358
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/f/fd/Flag_of_Senegal.svg/23px-Flag_of_Senegal.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/f/fd/Flag_of_Senegal.svg/35px-Flag_of_Senegal.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/f/fd/Flag_of_Senegal.svg/45px-Flag_of_Senegal.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Senegal
</td>
<td>5 years
</td>
<td><a href="/wiki/2017_Senegalese_parliamentary_election" title="2017 Senegalese parliamentary election"><span data-sort-value="000000002017-07-30-0000" style="white-space:nowrap">30 July 2017</span></a>
</td>
<td><span data-sort-value="000000002022-07-01-0000" style="white-space:nowrap">July 2022</span>
</td>
<td>
</td>
<td><a href="/wiki/2019_Senegalese_presidential_election" title="2019 Senegalese presidential election"><span data-sort-value="000000002019-02-24-0000" style="white-space:nowrap">24 February 2019</span></a>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>.315
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/f/fc/Flag_of_Seychelles.svg/23px-Flag_of_Seychelles.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/f/fc/Flag_of_Seychelles.svg/35px-Flag_of_Seychelles.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/f/fc/Flag_of_Seychelles.svg/46px-Flag_of_Seychelles.svg.png 2x" data-file-width="900" data-file-height="450">&nbsp;</span>Seychelles
</td>
<td>5 years
</td>
<td><a href="/wiki/2016_Seychellois_parliamentary_election" title="2016 Seychellois parliamentary election"><span data-sort-value="000000002016-09-08-0000" style="white-space:nowrap">8 September 2016</span></a>
</td>
<td><span data-sort-value="000000002021-10-01-0000" style="white-space:nowrap">October 2021</span>
</td>
<td>
</td>
<td><a href="/wiki/2015_Seychellois_presidential_election" title="2015 Seychellois presidential election"><span data-sort-value="000000002015-12-03-0000" style="white-space:nowrap">3 December 2015</span></a>
</td>
<td><span data-sort-value="000000002020-01-01-0000" style="white-space:nowrap">2020</span><sup id="cite_ref-6" class="reference"><a href="#cite_note-6">[6]</a></sup><sup id="cite_ref-7" class="reference"><a href="#cite_note-7">[7]</a></sup>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>no data
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/1/17/Flag_of_Sierra_Leone.svg/23px-Flag_of_Sierra_Leone.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/1/17/Flag_of_Sierra_Leone.svg/35px-Flag_of_Sierra_Leone.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/1/17/Flag_of_Sierra_Leone.svg/45px-Flag_of_Sierra_Leone.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Sierra Leone
</td>
<td>5 years
</td>
<td><a href="/wiki/2018_Sierra_Leonean_general_election" title="2018 Sierra Leonean general election"><span data-sort-value="000000002018-03-07-0000" style="white-space:nowrap">7 March 2018</span></a>
</td>
<td><span data-sort-value="000000002023-03-01-0000" style="white-space:nowrap">March 2023</span>
</td>
<td>
</td>
<td><a href="/wiki/2018_Sierra_Leonean_general_election" title="2018 Sierra Leonean general election"><span data-sort-value="000000002018-03-07-0000" style="white-space:nowrap">7 March 2018</span></a>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/Demography_of_Sierra_Leone" class="mw-redirect" title="Demography of Sierra Leone">6.1</a>
</td>
<td><a href="/wiki/Economy_of_Sierra_Leone" title="Economy of Sierra Leone">4</a>
</td>
<td>.210
</td>
<td><a href="/wiki/All_People%27s_Congress" title="All People's Congress">All People's Congress</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Flag_of_Somalia.svg/23px-Flag_of_Somalia.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Flag_of_Somalia.svg/35px-Flag_of_Somalia.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Flag_of_Somalia.svg/45px-Flag_of_Somalia.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Somalia
</td>
<td>4 years
</td>
<td><a href="/wiki/2016_Somali_parliamentary_election" title="2016 Somali parliamentary election"><span data-sort-value="000000002016-10-10-0000" style="white-space:nowrap">10 October 2016</span></a>
</td>
<td><span data-sort-value="000000002020-10-01-0000" style="white-space:nowrap">October 2020</span>
</td>
<td>5 years
</td>
<td><a href="/wiki/2017_Somali_presidential_election" title="2017 Somali presidential election"><span data-sort-value="000000002017-02-08-0000" style="white-space:nowrap">8 February 2017</span></a>
</td>
<td><a href="/w/index.php?title=2022_Somali_presidential_election&amp;action=edit&amp;redlink=1" class="new" title="2022 Somali presidential election (page does not exist)"><span data-sort-value="000000002022-01-01-0000" style="white-space:nowrap">2022</span></a>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Somalia" title="Demographics of Somalia">14</a>
</td>
<td><a href="/wiki/Economy_of_Somalia" title="Economy of Somalia">5.8</a>
</td>
<td>no data
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/a/af/Flag_of_South_Africa.svg/23px-Flag_of_South_Africa.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/a/af/Flag_of_South_Africa.svg/35px-Flag_of_South_Africa.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/a/af/Flag_of_South_Africa.svg/45px-Flag_of_South_Africa.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span><a href="/wiki/South_Africa" title="South Africa">South Africa</a>
</td>
<td>5 years<sup id="cite_ref-8" class="reference"><a href="#cite_note-8">[8]</a></sup>
</td>
<td><a href="/wiki/2019_South_African_general_election" title="2019 South African general election"><span data-sort-value="000000002019-05-08-0000" style="white-space:nowrap">8 May 2019</span></a>
</td>
<td><span data-sort-value="000000002024-05-01-0000" style="white-space:nowrap">May 2024</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_South_Africa" title="Demographics of South Africa">52.9</a>
</td>
<td><a href="/wiki/Economy_of_South_Africa" title="Economy of South Africa">375</a>
</td>
<td>no data
</td>
<td><a href="/wiki/African_National_Congress" title="African National Congress">ANC</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/0/01/Flag_of_Sudan.svg/23px-Flag_of_Sudan.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/0/01/Flag_of_Sudan.svg/35px-Flag_of_Sudan.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/0/01/Flag_of_Sudan.svg/46px-Flag_of_Sudan.svg.png 2x" data-file-width="1000" data-file-height="500">&nbsp;</span>Sudan
</td>
<td>5 years
</td>
<td><a href="/wiki/2015_Sudanese_general_election" title="2015 Sudanese general election"><span data-sort-value="000000002015-04-13-0000" style="white-space:nowrap">13 April 2015</span></a>
</td>
<td><span data-sort-value="000000002020-04-01-0000" style="white-space:nowrap">April 2020</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>no data
</td>
<td><a href="/wiki/National_Congress_(Sudan)" title="National Congress (Sudan)">National Congress</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/f/fb/Flag_of_Eswatini.svg/23px-Flag_of_Eswatini.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/f/fb/Flag_of_Eswatini.svg/35px-Flag_of_Eswatini.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/f/fb/Flag_of_Eswatini.svg/45px-Flag_of_Eswatini.svg.png 2x" data-file-width="450" data-file-height="300">&nbsp;</span>Swaziland
</td>
<td>5 years
</td>
<td><a href="/wiki/2018_Swazi_general_election" title="2018 Swazi general election"><span data-sort-value="000000002018-08-18-0000" style="white-space:nowrap">18 August 2018</span></a>
</td>
<td><span data-sort-value="000000002023-08-01-0000" style="white-space:nowrap">August 2023</span>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>Absolute monarchy.<br>Parliament has very limited powers.<br>Political parties are prohibited.
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>(no political parties; no <a href="/wiki/Responsible_government" title="Responsible government">responsible government</a>)
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/3/38/Flag_of_Tanzania.svg/23px-Flag_of_Tanzania.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/3/38/Flag_of_Tanzania.svg/35px-Flag_of_Tanzania.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/3/38/Flag_of_Tanzania.svg/45px-Flag_of_Tanzania.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Tanzania
</td>
<td>5 years
</td>
<td><a href="/wiki/2015_Tanzanian_general_election" title="2015 Tanzanian general election"><span data-sort-value="000000002015-10-25-0000" style="white-space:nowrap">25 October 2015</span></a>
</td>
<td><a href="/wiki/2020_Tanzanian_general_election" title="2020 Tanzanian general election"><span data-sort-value="000000002020-10-01-0000" style="white-space:nowrap">October 2020</span></a>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/Demography_of_Tanzania" class="mw-redirect" title="Demography of Tanzania">44.9</a>
</td>
<td><a href="/wiki/Economy_of_Tanzania" title="Economy of Tanzania">29</a>
</td>
<td>.346
</td>
<td><a href="/wiki/Chama_Cha_Mapinduzi" title="Chama Cha Mapinduzi">CCM</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/6/68/Flag_of_Togo.svg/23px-Flag_of_Togo.svg.png" decoding="async" width="23" height="14" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/6/68/Flag_of_Togo.svg/35px-Flag_of_Togo.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/6/68/Flag_of_Togo.svg/46px-Flag_of_Togo.svg.png 2x" data-file-width="809" data-file-height="500">&nbsp;</span>Togo
</td>
<td>5 years
</td>
<td><a href="/wiki/2018_Togolese_parliamentary_election" title="2018 Togolese parliamentary election"><span data-sort-value="000000002018-12-20-0000" style="white-space:nowrap">20 December 2018</span></a>
</td>
<td><span data-sort-value="000000002023-12-01-0000" style="white-space:nowrap">December 2023</span>
</td>
<td>5 years
</td>
<td><a href="/wiki/2015_Togolese_presidential_election" title="2015 Togolese presidential election"><span data-sort-value="000000002015-04-25-0000" style="white-space:nowrap">25 April 2015</span></a>
</td>
<td><span data-sort-value="000000002020-01-01-0000" style="white-space:nowrap">2020</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>.305
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Flag_of_Tunisia.svg/23px-Flag_of_Tunisia.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Flag_of_Tunisia.svg/35px-Flag_of_Tunisia.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Flag_of_Tunisia.svg/45px-Flag_of_Tunisia.svg.png 2x" data-file-width="1200" data-file-height="800">&nbsp;</span>Tunisia
</td>
<td>5 years
</td>
<td><a href="/wiki/2014_Tunisian_parliamentary_election" title="2014 Tunisian parliamentary election"><span data-sort-value="000000002014-10-26-0000" style="white-space:nowrap">26 October 2014</span></a>
</td>
<td><a href="/wiki/2019_Tunisian_parliamentary_election" title="2019 Tunisian parliamentary election"><span data-sort-value="000000002019-10-06-0000" style="white-space:nowrap">6 October 2019</span></a>
</td>
<td>5 years
</td>
<td><a href="/wiki/2014_Tunisian_presidential_election" title="2014 Tunisian presidential election"><span data-sort-value="000000002014-11-23-0000" style="white-space:nowrap">23 November 2014</span></a>
</td>
<td><a href="/wiki/2019_Tunisian_presidential_election" title="2019 Tunisian presidential election"><span data-sort-value="000000002019-11-10-0000" style="white-space:nowrap">10 November 2019</span></a>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Tunisia" title="Demographics of Tunisia">10.9</a>
</td>
<td><a href="/wiki/Economy_of_Tunisia" title="Economy of Tunisia">82</a>
</td>
<td>.721
</td>
<td>Coalition: <a href="/wiki/Nidaa_Tounes" title="Nidaa Tounes">Nidaa Tounes</a>,<br><a href="/wiki/Ennahda_Movement" title="Ennahda Movement">Ennahda Movement</a>,<br><a href="/wiki/Free_Patriotic_Union" title="Free Patriotic Union">Free Patriotic Union</a>, <a href="/wiki/Afek_Tounes" title="Afek Tounes">Afek Tounes</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Flag_of_Uganda.svg/23px-Flag_of_Uganda.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Flag_of_Uganda.svg/35px-Flag_of_Uganda.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Flag_of_Uganda.svg/45px-Flag_of_Uganda.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Uganda
</td>
<td>5 years
</td>
<td><a href="/wiki/2016_Ugandan_general_election" title="2016 Ugandan general election"><span data-sort-value="000000002016-02-18-0000" style="white-space:nowrap">18 February 2016</span></a>
</td>
<td><span data-sort-value="000000002021-02-01-0000" style="white-space:nowrap">February 2021</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/Demography_of_Uganda" class="mw-redirect" title="Demography of Uganda">35.8</a>
</td>
<td><a href="/wiki/Economy_of_Uganda" title="Economy of Uganda">21</a>
</td>
<td>.304
</td>
<td><a href="/wiki/National_Resistance_Movement" title="National Resistance Movement">National Resist.</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/0/06/Flag_of_Zambia.svg/23px-Flag_of_Zambia.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/0/06/Flag_of_Zambia.svg/35px-Flag_of_Zambia.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/0/06/Flag_of_Zambia.svg/45px-Flag_of_Zambia.svg.png 2x" data-file-width="2100" data-file-height="1400">&nbsp;</span>Zambia
</td>
<td>5 years
</td>
<td><a href="/wiki/2016_Zambian_general_election" title="2016 Zambian general election"><span data-sort-value="000000002016-08-11-0000" style="white-space:nowrap">11 August 2016</span></a>
</td>
<td><a href="/w/index.php?title=2021_Zambian_general_election&amp;action=edit&amp;redlink=1" class="new" title="2021 Zambian general election (page does not exist)"><span data-sort-value="000000002021-08-01-0000" style="white-space:nowrap">August 2021</span></a>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/Demography_of_Zambia" class="mw-redirect" title="Demography of Zambia">14.3</a>
</td>
<td><a href="/wiki/Economy_of_Zambia" title="Economy of Zambia">20</a>
</td>
<td>.283
</td>
<td><a href="/wiki/Patriotic_Front_(Zambia)" title="Patriotic Front (Zambia)">Patriotic Front</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/6/6a/Flag_of_Zimbabwe.svg/23px-Flag_of_Zimbabwe.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/6/6a/Flag_of_Zimbabwe.svg/35px-Flag_of_Zimbabwe.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/6/6a/Flag_of_Zimbabwe.svg/46px-Flag_of_Zimbabwe.svg.png 2x" data-file-width="1000" data-file-height="500">&nbsp;</span>Zimbabwe
</td>
<td>5 years
</td>
<td><a href="/wiki/2018_Zimbabwean_general_election" title="2018 Zimbabwean general election"><span data-sort-value="000000002018-07-30-0000" style="white-space:nowrap">30 July 2018</span></a>
</td>
<td><span data-sort-value="000000002023-07-01-0000" style="white-space:nowrap">July 2023</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/2018_Zimbabwean_general_election#Conduct" title="2018 Zimbabwean general election">Fraud</a>
</td>
<td><a href="/wiki/Demographics_of_Zimbabwe" title="Demographics of Zimbabwe">12.6</a>
</td>
<td><a href="/wiki/Economy_of_Zimbabwe" title="Economy of Zimbabwe">11</a>
</td>
<td>.284
</td>
<td><a href="/wiki/Zimbabwe_African_National_Union_%E2%80%93_Patriotic_Front" class="mw-redirect" title="Zimbabwe African National Union – Patriotic Front">Zanu-PF</a>
</td></tr></tbody><tfoot></tfoot></table>
<table class="wikitable sortable jquery-tablesorter" style="font-size:90%;">

<thead><tr>
<th rowspan="2" class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">Country
</th>
<th colspan="3">Parliamentary election
</th>
<th colspan="3">Presidential election
</th>
<th rowspan="2" class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending"><a href="/wiki/Unfair_election" title="Unfair election">Fairness</a>
</th>
<th rowspan="2" class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending"><a href="/wiki/List_of_countries_by_population" class="mw-redirect" title="List of countries by population">Pop.</a><br>(m)
</th>
<th rowspan="2" class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending"><a href="/wiki/List_of_countries_by_GDP_(nominal)" title="List of countries by GDP (nominal)">GDP</a><br>($bn)
</th>
<th rowspan="2" class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending"><a href="/wiki/List_of_countries_by_inequality-adjusted_HDI" title="List of countries by inequality-adjusted HDI">IHDI</a>
</th>
<th rowspan="2" class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">In power now
</th></tr><tr>
<th class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">Term
</th>
<th class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">Last election
</th>
<th class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">Next election
</th>
<th class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">Term
</th>
<th class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">Last election
</th>
<th class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">Next election
</th></tr></thead><tbody>

<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/8/89/Flag_of_Antigua_and_Barbuda.svg/23px-Flag_of_Antigua_and_Barbuda.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/8/89/Flag_of_Antigua_and_Barbuda.svg/35px-Flag_of_Antigua_and_Barbuda.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/8/89/Flag_of_Antigua_and_Barbuda.svg/45px-Flag_of_Antigua_and_Barbuda.svg.png 2x" data-file-width="690" data-file-height="460">&nbsp;</span>Antigua and Barbuda
</td>
<td>5 years
</td>
<td><a href="/w/index.php?title=2018_Antigua_and_Barbuda_general_election&amp;action=edit&amp;redlink=1" class="new" title="2018 Antigua and Barbuda general election (page does not exist)"><span data-sort-value="000000002018-03-21-0000" style="white-space:nowrap">21 March 2018</span></a>
</td>
<td><span data-sort-value="000000002023-03-01-0000" style="white-space:nowrap">March 2023</span>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>no data
</td>
<td><a href="/wiki/Antigua_Labour_Party" class="mw-redirect" title="Antigua Labour Party">Antigua Labour Party</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Flag_of_Argentina.svg/23px-Flag_of_Argentina.svg.png" decoding="async" width="23" height="14" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Flag_of_Argentina.svg/35px-Flag_of_Argentina.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Flag_of_Argentina.svg/46px-Flag_of_Argentina.svg.png 2x" data-file-width="800" data-file-height="500">&nbsp;</span>Argentina
</td>
<td>2 years
</td>
<td><a href="/wiki/2017_Argentine_legislative_election" title="2017 Argentine legislative election"><span data-sort-value="000000002017-10-22-0000" style="white-space:nowrap">22 October 2017</span></a>
</td>
<td><a href="/wiki/2019_Argentine_general_election" title="2019 Argentine general election"><span data-sort-value="000000002019-10-27-0000" style="white-space:nowrap">27 October 2019</span></a>
</td>
<td>4 years
</td>
<td><a href="/wiki/2015_Argentine_general_election" title="2015 Argentine general election"><span data-sort-value="000000002015-10-25-0000" style="white-space:nowrap">25 October 2015</span></a>
</td>
<td><a href="/wiki/2019_Argentine_general_election" title="2019 Argentine general election"><span data-sort-value="000000002019-10-27-0000" style="white-space:nowrap">27 October 2019</span></a>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Argentina" title="Demographics of Argentina">40.1</a>
</td>
<td><a href="/wiki/Economy_of_Argentina" title="Economy of Argentina">448</a>
</td>
<td>.653
</td>
<td><a href="/wiki/Cambiemos" class="mw-redirect" title="Cambiemos">Cambiemos</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/9/93/Flag_of_the_Bahamas.svg/23px-Flag_of_the_Bahamas.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/9/93/Flag_of_the_Bahamas.svg/35px-Flag_of_the_Bahamas.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/9/93/Flag_of_the_Bahamas.svg/46px-Flag_of_the_Bahamas.svg.png 2x" data-file-width="600" data-file-height="300">&nbsp;</span>Bahamas
</td>
<td>5 years
</td>
<td><a href="/wiki/2017_Bahamian_general_election" title="2017 Bahamian general election"><span data-sort-value="000000002017-05-10-0000" style="white-space:nowrap">10 May 2017</span></a>
</td>
<td><span data-sort-value="000000002022-05-01-0000" style="white-space:nowrap">May 2022</span>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>.658<sup id="cite_ref-UN2011_9-0" class="reference"><a href="#cite_note-UN2011-9">[9]</a></sup>
</td>
<td><a href="/wiki/Free_National_Movement" title="Free National Movement">Free National Movement</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/e/ef/Flag_of_Barbados.svg/23px-Flag_of_Barbados.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/e/ef/Flag_of_Barbados.svg/35px-Flag_of_Barbados.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/e/ef/Flag_of_Barbados.svg/45px-Flag_of_Barbados.svg.png 2x" data-file-width="1500" data-file-height="1000">&nbsp;</span>Barbados
</td>
<td>5 years
</td>
<td><a href="/wiki/2018_Barbadian_general_election" title="2018 Barbadian general election"><span data-sort-value="000000002018-05-24-0000" style="white-space:nowrap">24 May 2018</span></a>
</td>
<td><span data-sort-value="000000002023-05-01-0000" style="white-space:nowrap">May 2023</span>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>no data
</td>
<td><a href="/wiki/Barbados_Labour_Party" title="Barbados Labour Party">Barbados Labour Party</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Flag_of_Belize.svg/23px-Flag_of_Belize.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Flag_of_Belize.svg/35px-Flag_of_Belize.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Flag_of_Belize.svg/45px-Flag_of_Belize.svg.png 2x" data-file-width="750" data-file-height="500">&nbsp;</span>Belize
</td>
<td>5 years<sup id="cite_ref-10" class="reference"><a href="#cite_note-10">[10]</a></sup>
</td>
<td><a href="/wiki/2015_Belizean_general_election" title="2015 Belizean general election"><span data-sort-value="000000002015-11-04-0000" style="white-space:nowrap">4 November 2015</span></a>
</td>
<td><a href="/wiki/Next_Belizean_general_election" title="Next Belizean general election"><span data-sort-value="000000002021-02-01-0000" style="white-space:nowrap">February 2021</span></a>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Belize" title="Demographics of Belize">.312</a>
</td>
<td><a href="/wiki/Economy_of_Belize" title="Economy of Belize">1</a>
</td>
<td>no data
</td>
<td><a href="/wiki/United_Democratic_Party_(Belize)" title="United Democratic Party (Belize)">United Democratic Party</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/4/48/Flag_of_Bolivia.svg/22px-Flag_of_Bolivia.svg.png" decoding="async" width="22" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/4/48/Flag_of_Bolivia.svg/34px-Flag_of_Bolivia.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/4/48/Flag_of_Bolivia.svg/44px-Flag_of_Bolivia.svg.png 2x" data-file-width="1100" data-file-height="750">&nbsp;</span>Bolivia
</td>
<td>5 years
</td>
<td><a href="/wiki/2014_Bolivian_general_election" title="2014 Bolivian general election"><span data-sort-value="000000002014-10-12-0000" style="white-space:nowrap">12 October 2014</span></a>
</td>
<td><a href="/wiki/2019_Bolivian_general_election" title="2019 Bolivian general election"><span data-sort-value="000000002019-10-20-0000" style="white-space:nowrap">20 October 2019</span></a>
</td>
<td>5 years
</td>
<td><a href="/wiki/2014_Bolivian_general_election" title="2014 Bolivian general election"><span data-sort-value="000000002014-10-12-0000" style="white-space:nowrap">12 October 2014</span></a>
</td>
<td><span data-sort-value="000000002019-10-20-0000" style="white-space:nowrap">20 October 2019</span>
</td>
<td>
</td>
<td>10.5
</td>
<td><a href="/wiki/Economy_of_Bolivia" title="Economy of Bolivia">59</a>
</td>
<td>.444
</td>
<td><a href="/wiki/Movement_for_Socialism_%E2%80%93_Political_Instrument_for_the_Sovereignty_of_the_Peoples" class="mw-redirect" title="Movement for Socialism – Political Instrument for the Sovereignty of the Peoples">Movement for Socialism</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Flag_of_Bermuda.svg/23px-Flag_of_Bermuda.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Flag_of_Bermuda.svg/35px-Flag_of_Bermuda.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Flag_of_Bermuda.svg/46px-Flag_of_Bermuda.svg.png 2x" data-file-width="1000" data-file-height="500">&nbsp;</span>Bermuda
</td>
<td>5 years
</td>
<td><a href="/wiki/2017_Bermudian_general_election" title="2017 Bermudian general election"><span data-sort-value="000000002017-07-18-0000" style="white-space:nowrap">18 July 2017</span></a>
</td>
<td><a href="/wiki/Next_Bermudian_general_election" class="mw-redirect" title="Next Bermudian general election"><span data-sort-value="000000002022-07-01-0000" style="white-space:nowrap">July 2022</span></a>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>
</td>
<td>0.06
</td>
<td>5.5
</td>
<td>no data
</td>
<td><a href="/wiki/One_Bermuda_Alliance" title="One Bermuda Alliance">One Bermuda Alliance</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/en/thumb/0/05/Flag_of_Brazil.svg/22px-Flag_of_Brazil.svg.png" decoding="async" width="22" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/en/thumb/0/05/Flag_of_Brazil.svg/33px-Flag_of_Brazil.svg.png 1.5x, //upload.wikimedia.org/wikipedia/en/thumb/0/05/Flag_of_Brazil.svg/43px-Flag_of_Brazil.svg.png 2x" data-file-width="720" data-file-height="504">&nbsp;</span>Brazil
</td>
<td>4 years<sup id="cite_ref-Brazilian_Constitution_11-0" class="reference"><a href="#cite_note-Brazilian_Constitution-11">[11]</a></sup>
</td>
<td><a href="/wiki/2018_Brazilian_general_election" title="2018 Brazilian general election"><span data-sort-value="000000002018-10-07-0000" style="white-space:nowrap">7 October 2018</span></a>
</td>
<td><a href="/w/index.php?title=2022_Brazilian_general_election&amp;action=edit&amp;redlink=1" class="new" title="2022 Brazilian general election (page does not exist)"><span data-sort-value="000000002022-10-01-0000" style="white-space:nowrap">October 2022</span></a>
</td>
<td>4 years<sup id="cite_ref-Brazilian_Constitution_11-1" class="reference"><a href="#cite_note-Brazilian_Constitution-11">[11]</a></sup>
</td>
<td><a href="/wiki/2018_Brazilian_general_election" title="2018 Brazilian general election"><span data-sort-value="000000002018-10-07-0000" style="white-space:nowrap">7 October 2018</span></a>
</td>
<td><a href="/w/index.php?title=2022_Brazilian_general_election&amp;action=edit&amp;redlink=1" class="new" title="2022 Brazilian general election (page does not exist)"><span data-sort-value="000000002022-10-01-0000" style="white-space:nowrap">October 2022</span></a>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Brazil" title="Demographics of Brazil">193.9</a>
</td>
<td><a href="/wiki/Economy_of_Brazil" title="Economy of Brazil">2,476</a>
</td>
<td>.531
</td>
<td><a href="/wiki/Social_Liberal_Party_(Brazil)" title="Social Liberal Party (Brazil)">Social Liberal Party</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Flag_of_Canada_%28Pantone%29.svg/23px-Flag_of_Canada_%28Pantone%29.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Flag_of_Canada_%28Pantone%29.svg/35px-Flag_of_Canada_%28Pantone%29.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Flag_of_Canada_%28Pantone%29.svg/46px-Flag_of_Canada_%28Pantone%29.svg.png 2x" data-file-width="1200" data-file-height="600">&nbsp;</span>Canada
</td>
<td>4 years<sup id="cite_ref-12" class="reference"><a href="#cite_note-12">[12]</a></sup>
</td>
<td><a href="/wiki/42nd_Canadian_federal_election" class="mw-redirect" title="42nd Canadian federal election"><span data-sort-value="000000002015-10-19-0000" style="white-space:nowrap">19 October 2015</span></a>
</td>
<td><a href="/wiki/43rd_Canadian_federal_election" class="mw-redirect" title="43rd Canadian federal election"><span data-sort-value="000000002019-10-21-0000" style="white-space:nowrap">21 October 2019</span></a>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Canada" title="Demographics of Canada">35.1</a>
</td>
<td><a href="/wiki/Economy_of_Canada" title="Economy of Canada">1,736</a>
</td>
<td>.832
</td>
<td><a href="/wiki/Liberal_Party_(Canada)" class="mw-redirect" title="Liberal Party (Canada)">Liberal Party</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Flag_of_the_Cayman_Islands.svg/23px-Flag_of_the_Cayman_Islands.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Flag_of_the_Cayman_Islands.svg/35px-Flag_of_the_Cayman_Islands.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Flag_of_the_Cayman_Islands.svg/46px-Flag_of_the_Cayman_Islands.svg.png 2x" data-file-width="1200" data-file-height="600">&nbsp;</span>Cayman Islands
</td>
<td>4 years
</td>
<td><a href="/wiki/2017_Caymanian_general_election" title="2017 Caymanian general election"><span data-sort-value="000000002017-05-24-0000" style="white-space:nowrap">24 May 2017</span></a>
</td>
<td><span data-sort-value="000000002021-05-01-0000" style="white-space:nowrap">May 2021</span>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_the_Cayman_Islands" title="Demographics of the Cayman Islands">0.06</a>
</td>
<td>3.48
</td>
<td>no data
</td>
<td><a href="/wiki/People%27s_Progressive_Movement_(Cayman_Islands)" title="People's Progressive Movement (Cayman Islands)">People's Progressive Movement</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/7/78/Flag_of_Chile.svg/23px-Flag_of_Chile.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/7/78/Flag_of_Chile.svg/35px-Flag_of_Chile.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/7/78/Flag_of_Chile.svg/45px-Flag_of_Chile.svg.png 2x" data-file-width="1500" data-file-height="1000">&nbsp;</span>Chile
</td>
<td>4 years
</td>
<td><a href="/wiki/2017_Chilean_general_election" title="2017 Chilean general election"><span data-sort-value="000000002017-11-19-0000" style="white-space:nowrap">19 November 2017</span></a>
</td>
<td><span data-sort-value="000000002021-11-01-0000" style="white-space:nowrap">November 2021</span>
</td>
<td>4 years
</td>
<td><a href="/wiki/2017_Chilean_general_election" title="2017 Chilean general election"><span data-sort-value="000000002017-11-19-0000" style="white-space:nowrap">19 November 2017</span></a>
</td>
<td><span data-sort-value="000000002021-01-01-0000" style="white-space:nowrap">2021</span>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Chile" title="Demographics of Chile">16.6</a>
</td>
<td><a href="/wiki/Economy_of_Chile" title="Economy of Chile">248</a>
</td>
<td>.664
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/2/21/Flag_of_Colombia.svg/23px-Flag_of_Colombia.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/2/21/Flag_of_Colombia.svg/35px-Flag_of_Colombia.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/2/21/Flag_of_Colombia.svg/45px-Flag_of_Colombia.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Colombia
</td>
<td>4 years
</td>
<td><a href="/wiki/2018_Colombian_parliamentary_election" title="2018 Colombian parliamentary election"><span data-sort-value="000000002018-03-11-0000" style="white-space:nowrap">11 March 2018</span></a>
</td>
<td><span data-sort-value="000000002022-03-01-0000" style="white-space:nowrap">March 2022</span>
</td>
<td>4 years
</td>
<td><a href="/wiki/2018_Colombian_presidential_election" title="2018 Colombian presidential election"><span data-sort-value="000000002018-05-27-0000" style="white-space:nowrap">27 May 2018</span></a>
</td>
<td><span data-sort-value="000000002022-01-01-0000" style="white-space:nowrap">2022</span>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Colombia" title="Demographics of Colombia">47.2</a>
</td>
<td><a href="/wiki/Economy_of_Colombia" title="Economy of Colombia">333</a>
</td>
<td>.519
</td>
<td><a href="/wiki/Social_Party_of_National_Unity" title="Social Party of National Unity">Social Party</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Flag_of_Costa_Rica.svg/23px-Flag_of_Costa_Rica.svg.png" decoding="async" width="23" height="14" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Flag_of_Costa_Rica.svg/35px-Flag_of_Costa_Rica.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Flag_of_Costa_Rica.svg/46px-Flag_of_Costa_Rica.svg.png 2x" data-file-width="1000" data-file-height="600">&nbsp;</span>Costa Rica
</td>
<td>4 years
</td>
<td><a href="/wiki/2018_Costa_Rican_general_election" title="2018 Costa Rican general election"><span data-sort-value="000000002018-02-04-0000" style="white-space:nowrap">4 February 2018</span></a>
</td>
<td><span data-sort-value="000000002022-02-01-0000" style="white-space:nowrap">February 2022</span>
</td>
<td>4 years
</td>
<td><a href="/wiki/2018_Costa_Rican_general_election" title="2018 Costa Rican general election"><span data-sort-value="000000002018-02-04-0000" style="white-space:nowrap">4 February 2018</span></a>
</td>
<td><span data-sort-value="000000002022-02-01-0000" style="white-space:nowrap">February 2022</span>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Costa_Rica" title="Demographics of Costa Rica">4.6</a>
</td>
<td><a href="/wiki/Economy_of_Costa_Rica" title="Economy of Costa Rica">41</a>
</td>
<td>.606
</td>
<td><a href="/wiki/National_Liberation_Party_(Costa_Rica)" title="National Liberation Party (Costa Rica)">National Liberation</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/b/bd/Flag_of_Cuba.svg/23px-Flag_of_Cuba.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/b/bd/Flag_of_Cuba.svg/35px-Flag_of_Cuba.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/b/bd/Flag_of_Cuba.svg/46px-Flag_of_Cuba.svg.png 2x" data-file-width="800" data-file-height="400">&nbsp;</span>Cuba
</td>
<td>5 years
</td>
<td><a href="/wiki/2018_Cuban_parliamentary_election" title="2018 Cuban parliamentary election"><span data-sort-value="000000002018-03-11-0000" style="white-space:nowrap">11 March 2018</span></a>
</td>
<td><a href="/wiki/2023_Cuban_parliamentary_election" title="2023 Cuban parliamentary election"><span data-sort-value="000000002023-01-01-0000" style="white-space:nowrap">2023</span></a>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>no data
</td>
<td><a href="/wiki/Communist_Party_of_Cuba" title="Communist Party of Cuba">Communist Party of Cuba</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Flag_of_Dominica.svg/23px-Flag_of_Dominica.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Flag_of_Dominica.svg/35px-Flag_of_Dominica.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Flag_of_Dominica.svg/46px-Flag_of_Dominica.svg.png 2x" data-file-width="1200" data-file-height="600">&nbsp;</span>Dominica
</td>
<td>5 years
</td>
<td><a href="/wiki/2014_Dominican_general_election" title="2014 Dominican general election"><span data-sort-value="000000002014-12-08-0000" style="white-space:nowrap">8 December 2014</span></a>
</td>
<td><a href="/wiki/2019_Dominican_general_election" title="2019 Dominican general election"><span data-sort-value="000000002019-12-01-0000" style="white-space:nowrap">December 2019</span></a>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>no data
</td>
<td><a href="/wiki/Dominica_Labour_Party" title="Dominica Labour Party">Dominica Labour Party</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Flag_of_the_Dominican_Republic.svg/23px-Flag_of_the_Dominican_Republic.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Flag_of_the_Dominican_Republic.svg/35px-Flag_of_the_Dominican_Republic.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Flag_of_the_Dominican_Republic.svg/45px-Flag_of_the_Dominican_Republic.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Dominican Republic
</td>
<td>4 years
</td>
<td><a href="/wiki/2016_Dominican_Republic_general_election" title="2016 Dominican Republic general election"><span data-sort-value="000000002016-05-15-0000" style="white-space:nowrap">15 May 2016</span></a>
</td>
<td><a href="/wiki/2020_Dominican_Republic_general_election" title="2020 Dominican Republic general election"><span data-sort-value="000000002020-05-01-0000" style="white-space:nowrap">May 2020</span></a>
</td>
<td>4 years
</td>
<td><a href="/wiki/2016_Dominican_Republic_general_election" title="2016 Dominican Republic general election"><span data-sort-value="000000002016-05-15-0000" style="white-space:nowrap">15 May 2016</span></a>
</td>
<td><a href="/wiki/2020_Dominican_Republic_general_election" title="2020 Dominican Republic general election"><span data-sort-value="000000002020-05-01-0000" style="white-space:nowrap">May 2020</span></a>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_the_Dominican_Republic" title="Demographics of the Dominican Republic">9.4</a>
</td>
<td><a href="/wiki/Economy_of_the_Dominican_Republic" title="Economy of the Dominican Republic">98.7</a>
</td>
<td>.510
</td>
<td><a href="/wiki/Dominican_Liberation_Party" title="Dominican Liberation Party">Dominican Liberation Party</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Flag_of_Ecuador.svg/23px-Flag_of_Ecuador.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Flag_of_Ecuador.svg/35px-Flag_of_Ecuador.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Flag_of_Ecuador.svg/45px-Flag_of_Ecuador.svg.png 2x" data-file-width="1440" data-file-height="960">&nbsp;</span>Ecuador
</td>
<td>4 years
</td>
<td><a href="/wiki/2017_Ecuadorian_general_election" title="2017 Ecuadorian general election"><span data-sort-value="000000002017-02-19-0000" style="white-space:nowrap">19 February 2017</span></a>
</td>
<td><span data-sort-value="000000002021-02-01-0000" style="white-space:nowrap">February 2021</span>
</td>
<td>4 years
</td>
<td><a href="/wiki/2017_Ecuadorian_general_election" title="2017 Ecuadorian general election"><span data-sort-value="000000002017-02-19-0000" style="white-space:nowrap">19 February 2017</span></a>
</td>
<td><span data-sort-value="000000002021-02-01-0000" style="white-space:nowrap">February 2021</span>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Ecuador" class="mw-redirect" title="Demographics of Ecuador">15.5</a>
</td>
<td><a href="/wiki/Economy_of_Ecuador" title="Economy of Ecuador">66</a>
</td>
<td>.537
</td>
<td><a href="/wiki/PAIS_Alliance" title="PAIS Alliance">PAIS Alliance</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/3/34/Flag_of_El_Salvador.svg/23px-Flag_of_El_Salvador.svg.png" decoding="async" width="23" height="14" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/3/34/Flag_of_El_Salvador.svg/35px-Flag_of_El_Salvador.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/3/34/Flag_of_El_Salvador.svg/46px-Flag_of_El_Salvador.svg.png 2x" data-file-width="1000" data-file-height="600">&nbsp;</span><a href="/wiki/El_Salvador" title="El Salvador">El Salvador</a>
</td>
<td>3 years
</td>
<td><a href="/wiki/2018_Salvadoran_legislative_election" title="2018 Salvadoran legislative election"><span data-sort-value="000000002018-03-04-0000" style="white-space:nowrap">4 March 2018</span></a>
</td>
<td><span data-sort-value="000000002021-03-01-0000" style="white-space:nowrap">March 2021</span>
</td>
<td>5 years
</td>
<td><a href="/wiki/2014_Salvadoran_presidential_election" title="2014 Salvadoran presidential election"><span data-sort-value="000000002019-02-03-0000" style="white-space:nowrap">3 February 2019</span></a>
</td>
<td><span data-sort-value="000000002024-01-01-0000" style="white-space:nowrap">2024</span>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_El_Salvador" title="Demographics of El Salvador">6.1</a>
</td>
<td><a href="/wiki/Economy_of_El_Salvador" title="Economy of El Salvador">23</a>
</td>
<td>.499
</td>
<td><a href="/wiki/Farabundo_Mart%C3%AD_National_Liberation_Front" title="Farabundo Martí National Liberation Front">National Liberation</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/8/83/Flag_of_the_Falkland_Islands.svg/23px-Flag_of_the_Falkland_Islands.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/8/83/Flag_of_the_Falkland_Islands.svg/35px-Flag_of_the_Falkland_Islands.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/8/83/Flag_of_the_Falkland_Islands.svg/46px-Flag_of_the_Falkland_Islands.svg.png 2x" data-file-width="1200" data-file-height="600">&nbsp;</span>Falkland Islands
</td>
<td>4 years
</td>
<td><a href="/wiki/2017_Falkland_Islands_general_election" title="2017 Falkland Islands general election"><span data-sort-value="000000002017-11-09-0000" style="white-space:nowrap">9 November 2017</span></a>
</td>
<td><a href="/wiki/2021_Falkland_Islands_general_election" class="mw-redirect" title="2021 Falkland Islands general election"><span data-sort-value="000000002021-11-01-0000" style="white-space:nowrap">November 2021</span></a>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_the_Falkland_Islands" class="mw-redirect" title="Demographics of the Falkland Islands">.0026</a>
</td>
<td><a href="/wiki/Economy_of_the_Falkland_Islands" title="Economy of the Falkland Islands">.1645</a>
</td>
<td>.874
</td>
<td><a href="/wiki/Non-partisan_democracy" title="Non-partisan democracy">Non-partisan Coalition</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Flag_of_Grenada.svg/23px-Flag_of_Grenada.svg.png" decoding="async" width="23" height="14" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Flag_of_Grenada.svg/35px-Flag_of_Grenada.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Flag_of_Grenada.svg/46px-Flag_of_Grenada.svg.png 2x" data-file-width="600" data-file-height="360">&nbsp;</span>Grenada
</td>
<td>5 years
</td>
<td><a href="/wiki/2018_Grenadian_general_election" title="2018 Grenadian general election"><span data-sort-value="000000002018-03-13-0000" style="white-space:nowrap">13 March 2018</span></a>
</td>
<td><span data-sort-value="000000002023-03-01-0000" style="white-space:nowrap">March 2023</span>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>no data
</td>
<td><a href="/wiki/New_National_Party_(Grenada)" title="New National Party (Grenada)">New National Party</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Flag_of_Guatemala.svg/23px-Flag_of_Guatemala.svg.png" decoding="async" width="23" height="14" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Flag_of_Guatemala.svg/35px-Flag_of_Guatemala.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Flag_of_Guatemala.svg/46px-Flag_of_Guatemala.svg.png 2x" data-file-width="960" data-file-height="600">&nbsp;</span>Guatemala
</td>
<td>4 years
</td>
<td><a href="/wiki/2015_Guatemalan_general_election" title="2015 Guatemalan general election"><span data-sort-value="000000002019-06-16-0000" style="white-space:nowrap">16 June 2019</span></a>
</td>
<td><a href="/wiki/2019_Guatemalan_general_election" title="2019 Guatemalan general election"><span data-sort-value="000000002023-01-01-0000" style="white-space:nowrap">2023</span></a>
</td>
<td>4 years
</td>
<td><a href="/wiki/2015_Guatemalan_general_election" title="2015 Guatemalan general election"><span data-sort-value="000000002019-06-16-0000" style="white-space:nowrap">16 June 2019</span></a>
</td>
<td><a href="/wiki/2019_Guatemalan_general_election" title="2019 Guatemalan general election"><span data-sort-value="000000002023-01-01-0000" style="white-space:nowrap">2023</span></a>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Guatemala" title="Demographics of Guatemala">15.4</a>
</td>
<td><a href="/wiki/Economy_of_Guatemala" title="Economy of Guatemala">46</a>
</td>
<td>.389
</td>
<td><a href="/wiki/Renewed_Democratic_Liberty" title="Renewed Democratic Liberty">Renewed Democratic Liberty</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/9/99/Flag_of_Guyana.svg/23px-Flag_of_Guyana.svg.png" decoding="async" width="23" height="14" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/9/99/Flag_of_Guyana.svg/35px-Flag_of_Guyana.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/9/99/Flag_of_Guyana.svg/46px-Flag_of_Guyana.svg.png 2x" data-file-width="500" data-file-height="300">&nbsp;</span>Guyana
</td>
<td>5 years
</td>
<td><a href="/wiki/2015_Guyanese_general_election" title="2015 Guyanese general election"><span data-sort-value="000000002015-05-11-0000" style="white-space:nowrap">11 May 2015</span></a>
</td>
<td><a href="/wiki/2019_Guyanese_general_election" title="2019 Guyanese general election"><span data-sort-value="000000002019-01-01-0000" style="white-space:nowrap">2019</span></a>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>.514
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/5/56/Flag_of_Haiti.svg/23px-Flag_of_Haiti.svg.png" decoding="async" width="23" height="14" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/5/56/Flag_of_Haiti.svg/35px-Flag_of_Haiti.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/5/56/Flag_of_Haiti.svg/46px-Flag_of_Haiti.svg.png 2x" data-file-width="1000" data-file-height="600">&nbsp;</span>Haiti
</td>
<td>4 years
</td>
<td><a href="/wiki/Haitian_Senate_election,_2016%E2%80%9317" class="mw-redirect" title="Haitian Senate election, 2016–17"><span data-sort-value="000000002016-11-20-0000" style="white-space:nowrap">20 November 2016</span></a>
</td>
<td><a href="/wiki/2019_Haitian_parliamentary_election" title="2019 Haitian parliamentary election"><span data-sort-value="000000002019-10-01-0000" style="white-space:nowrap">October 2019</span></a>
</td>
<td>
</td>
<td><a href="/wiki/November_2016_Haitian_presidential_election" title="November 2016 Haitian presidential election"><span data-sort-value="000000002016-11-20-0000" style="white-space:nowrap">20 November 2016</span></a>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>.273
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/8/82/Flag_of_Honduras.svg/23px-Flag_of_Honduras.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/8/82/Flag_of_Honduras.svg/35px-Flag_of_Honduras.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/8/82/Flag_of_Honduras.svg/46px-Flag_of_Honduras.svg.png 2x" data-file-width="1000" data-file-height="500">&nbsp;</span>Honduras
</td>
<td>4 years
</td>
<td><a href="/wiki/2017_Honduran_general_election" title="2017 Honduran general election"><span data-sort-value="000000002017-11-26-0000" style="white-space:nowrap">26 November 2017</span></a>
</td>
<td><span data-sort-value="000000002021-11-01-0000" style="white-space:nowrap">November 2021</span>
</td>
<td>4 years
</td>
<td><a href="/wiki/2017_Honduran_general_election" title="2017 Honduran general election"><span data-sort-value="000000002017-11-26-0000" style="white-space:nowrap">26 November 2017</span></a>
</td>
<td><span data-sort-value="000000002021-11-01-0000" style="white-space:nowrap">November 2021</span>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Honduras" title="Demographics of Honduras">8.3</a>
</td>
<td><a href="/wiki/Economy_of_Honduras" title="Economy of Honduras">17</a>
</td>
<td>.458
</td>
<td><a href="/wiki/National_Party_of_Honduras" title="National Party of Honduras">National</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Flag_of_Jamaica.svg/23px-Flag_of_Jamaica.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Flag_of_Jamaica.svg/35px-Flag_of_Jamaica.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Flag_of_Jamaica.svg/46px-Flag_of_Jamaica.svg.png 2x" data-file-width="600" data-file-height="300">&nbsp;</span>Jamaica
</td>
<td>5 years
</td>
<td><a href="/wiki/2016_Jamaican_general_election" title="2016 Jamaican general election"><span data-sort-value="000000002016-02-25-0000" style="white-space:nowrap">25 February 2016</span></a>
</td>
<td><span data-sort-value="000000002021-02-01-0000" style="white-space:nowrap">February 2021</span>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>.591
</td>
<td><a href="/wiki/Jamaica_Labour_Party" title="Jamaica Labour Party">Jamaica Labour Party</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/f/fc/Flag_of_Mexico.svg/23px-Flag_of_Mexico.svg.png" decoding="async" width="23" height="13" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/f/fc/Flag_of_Mexico.svg/35px-Flag_of_Mexico.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/f/fc/Flag_of_Mexico.svg/46px-Flag_of_Mexico.svg.png 2x" data-file-width="980" data-file-height="560">&nbsp;</span>Mexico
</td>
<td>3 years
</td>
<td><a href="/wiki/2018_Mexican_general_election" title="2018 Mexican general election"><span data-sort-value="000000002018-07-01-0000" style="white-space:nowrap">1 July 2018</span></a>
</td>
<td><a href="/wiki/2021_Mexican_legislative_election" title="2021 Mexican legislative election"><span data-sort-value="000000002021-07-01-0000" style="white-space:nowrap">July 2021</span></a>
</td>
<td>6 years
</td>
<td><a href="/wiki/2018_Mexican_general_election" title="2018 Mexican general election"><span data-sort-value="000000002018-07-01-0000" style="white-space:nowrap">1 July 2018</span></a>
</td>
<td><a href="/w/index.php?title=2024_Mexican_presidential_election&amp;action=edit&amp;redlink=1" class="new" title="2024 Mexican presidential election (page does not exist)"><span data-sort-value="000000002024-01-01-0000" style="white-space:nowrap">2024</span></a>
</td>
<td>Violence, Drug War
</td>
<td><a href="/wiki/Demographics_of_Mexico" title="Demographics of Mexico">117.4</a>
</td>
<td><a href="/wiki/Economy_of_Mexico" title="Economy of Mexico">1,155</a>
</td>
<td>.593
</td>
<td><a href="/wiki/Movimiento_Regeneraci%C3%B3n_Nacional" class="mw-redirect" title="Movimiento Regeneración Nacional">MORENA</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/1/19/Flag_of_Nicaragua.svg/23px-Flag_of_Nicaragua.svg.png" decoding="async" width="23" height="14" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/1/19/Flag_of_Nicaragua.svg/35px-Flag_of_Nicaragua.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/1/19/Flag_of_Nicaragua.svg/46px-Flag_of_Nicaragua.svg.png 2x" data-file-width="1000" data-file-height="600">&nbsp;</span>Nicaragua
</td>
<td>5 years
</td>
<td><a href="/wiki/2016_Nicaraguan_general_election" title="2016 Nicaraguan general election"><span data-sort-value="000000002016-11-06-0000" style="white-space:nowrap">6 November 2016</span></a>
</td>
<td><a href="/w/index.php?title=2021_Nicaraguan_general_election&amp;action=edit&amp;redlink=1" class="new" title="2021 Nicaraguan general election (page does not exist)"><span data-sort-value="000000002021-11-01-0000" style="white-space:nowrap">November 2021</span></a>
</td>
<td>5 years
</td>
<td><a href="/wiki/2016_Nicaraguan_general_election" title="2016 Nicaraguan general election"><span data-sort-value="000000002016-11-06-0000" style="white-space:nowrap">6 November 2016</span></a>
</td>
<td><a href="/w/index.php?title=2021_Nicaraguan_general_election&amp;action=edit&amp;redlink=1" class="new" title="2021 Nicaraguan general election (page does not exist)"><span data-sort-value="000000002021-01-01-0000" style="white-space:nowrap">2021</span></a>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Nicaragua" title="Demographics of Nicaragua">6.0</a>
</td>
<td><a href="/wiki/Economy_of_Nicaragua" title="Economy of Nicaragua">7</a>
</td>
<td>.434
</td>
<td><a href="/wiki/Sandinista_National_Liberation_Front" title="Sandinista National Liberation Front">Sandinista</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Flag_of_Panama.svg/23px-Flag_of_Panama.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Flag_of_Panama.svg/35px-Flag_of_Panama.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Flag_of_Panama.svg/45px-Flag_of_Panama.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Panama
</td>
<td>5 years
</td>
<td><a href="/wiki/2019_Panamanian_general_election" title="2019 Panamanian general election"><span data-sort-value="000000002019-05-05-0000" style="white-space:nowrap">5 May 2019</span></a>
</td>
<td><span data-sort-value="000000002024-05-01-0000" style="white-space:nowrap">May 2024</span>
</td>
<td>5 years
</td>
<td><a href="/wiki/2014_Panamanian_general_election" title="2014 Panamanian general election"><span data-sort-value="000000002014-05-04-0000" style="white-space:nowrap">4 May 2014</span></a>
</td>
<td><span data-sort-value="000000002019-01-01-0000" style="white-space:nowrap">2019</span>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Panama" title="Demographics of Panama">3.4</a>
</td>
<td><a href="/wiki/Economy_of_Panama" title="Economy of Panama">30</a>
</td>
<td>.588
</td>
<td><a href="/wiki/Democratic_Change_(Panama)" title="Democratic Change (Panama)">Democratic Change</a>/Coal.
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/2/27/Flag_of_Paraguay.svg/23px-Flag_of_Paraguay.svg.png" decoding="async" width="23" height="13" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/2/27/Flag_of_Paraguay.svg/35px-Flag_of_Paraguay.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/2/27/Flag_of_Paraguay.svg/46px-Flag_of_Paraguay.svg.png 2x" data-file-width="1000" data-file-height="550">&nbsp;</span>Paraguay
</td>
<td>5 years
</td>
<td><a href="/wiki/2018_Paraguayan_general_election" title="2018 Paraguayan general election"><span data-sort-value="000000002018-04-22-0000" style="white-space:nowrap">22 April 2018</span></a>
</td>
<td><span data-sort-value="000000002023-04-01-0000" style="white-space:nowrap">April 2023</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>.505<sup id="cite_ref-UN2011_9-1" class="reference"><a href="#cite_note-UN2011-9">[9]</a></sup>
</td>
<td><a href="/wiki/Colorado_Party_(Paraguay)" title="Colorado Party (Paraguay)">Colorado</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/c/cf/Flag_of_Peru.svg/23px-Flag_of_Peru.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/c/cf/Flag_of_Peru.svg/35px-Flag_of_Peru.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/c/cf/Flag_of_Peru.svg/45px-Flag_of_Peru.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Peru
</td>
<td>5 years
</td>
<td><a href="/wiki/2016_Peruvian_general_election" title="2016 Peruvian general election"><span data-sort-value="000000002016-04-10-0000" style="white-space:nowrap">10 April 2016</span></a>
</td>
<td><a href="/w/index.php?title=2021_Peruvian_general_election&amp;action=edit&amp;redlink=1" class="new" title="2021 Peruvian general election (page does not exist)"><span data-sort-value="000000002021-04-01-0000" style="white-space:nowrap">April 2021</span></a>
</td>
<td>5 years
</td>
<td><a href="/wiki/2016_Peruvian_general_election" title="2016 Peruvian general election"><span data-sort-value="000000002016-04-10-0000" style="white-space:nowrap">10 April 2016</span></a>
</td>
<td><a href="/w/index.php?title=2021_Peruvian_general_election&amp;action=edit&amp;redlink=1" class="new" title="2021 Peruvian general election (page does not exist)"><span data-sort-value="000000002021-01-01-0000" style="white-space:nowrap">2021</span></a>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Peru" title="Demographics of Peru">30.4</a>
</td>
<td><a href="/wiki/Economy_of_Peru" title="Economy of Peru">180</a>
</td>
<td>.561
</td>
<td><a href="/wiki/Gana_Per%C3%BA" class="mw-redirect" title="Gana Perú">Gana Perú</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/2/28/Flag_of_Puerto_Rico.svg/23px-Flag_of_Puerto_Rico.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/2/28/Flag_of_Puerto_Rico.svg/35px-Flag_of_Puerto_Rico.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/2/28/Flag_of_Puerto_Rico.svg/45px-Flag_of_Puerto_Rico.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Puerto Rico
</td>
<td>4 years
</td>
<td><a href="/wiki/2016_Puerto_Rican_general_election" title="2016 Puerto Rican general election"><span data-sort-value="000000002016-11-08-0000" style="white-space:nowrap">8 November 2016</span></a>
</td>
<td><a href="/wiki/2020_Puerto_Rico_gubernatorial_election" class="mw-redirect" title="2020 Puerto Rico gubernatorial election"><span data-sort-value="000000002020-11-01-0000" style="white-space:nowrap">November 2020</span></a>
</td>
<td>4 years
</td>
<td><a href="/wiki/2016_Puerto_Rican_general_election" title="2016 Puerto Rican general election"><span data-sort-value="000000002016-11-08-0000" style="white-space:nowrap">8 November 2016</span></a>
</td>
<td><a href="/wiki/2020_Puerto_Rico_gubernatorial_election" class="mw-redirect" title="2020 Puerto Rico gubernatorial election"><span data-sort-value="000000002020-11-01-0000" style="white-space:nowrap">November 2020</span></a>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Puerto_Rico" title="Demographics of Puerto Rico">3.7</a>
</td>
<td><a href="/wiki/Economy_of_Puerto_Rico" title="Economy of Puerto Rico">102</a>
</td>
<td>0.905
</td>
<td><a href="/wiki/New_Progressive_Party_(Puerto_Rico)" title="New Progressive Party (Puerto Rico)">New Progressive Party</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/f/fe/Flag_of_Saint_Kitts_and_Nevis.svg/23px-Flag_of_Saint_Kitts_and_Nevis.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/f/fe/Flag_of_Saint_Kitts_and_Nevis.svg/35px-Flag_of_Saint_Kitts_and_Nevis.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/f/fe/Flag_of_Saint_Kitts_and_Nevis.svg/45px-Flag_of_Saint_Kitts_and_Nevis.svg.png 2x" data-file-width="750" data-file-height="500">&nbsp;</span>Saint Kitts and Nevis
</td>
<td>5 years
</td>
<td><a href="/wiki/2015_Saint_Kitts_and_Nevis_general_election" title="2015 Saint Kitts and Nevis general election"><span data-sort-value="000000002015-02-16-0000" style="white-space:nowrap">16 February 2015</span></a>
</td>
<td><span data-sort-value="000000002020-02-01-0000" style="white-space:nowrap">February 2020</span>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>no data
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Flag_of_Saint_Lucia.svg/23px-Flag_of_Saint_Lucia.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Flag_of_Saint_Lucia.svg/35px-Flag_of_Saint_Lucia.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Flag_of_Saint_Lucia.svg/46px-Flag_of_Saint_Lucia.svg.png 2x" data-file-width="1200" data-file-height="600">&nbsp;</span>Saint Lucia
</td>
<td>5 years
</td>
<td><a href="/wiki/2016_Saint_Lucian_general_election" title="2016 Saint Lucian general election"><span data-sort-value="000000002016-06-06-0000" style="white-space:nowrap">6 June 2016</span></a>
</td>
<td><span data-sort-value="000000002021-06-01-0000" style="white-space:nowrap">June 2021</span>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>no data
</td>
<td><a href="/wiki/United_Workers_Party_(Saint_Lucia)" title="United Workers Party (Saint Lucia)">United Workers Party</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Flag_of_Saint_Vincent_and_the_Grenadines.svg/23px-Flag_of_Saint_Vincent_and_the_Grenadines.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Flag_of_Saint_Vincent_and_the_Grenadines.svg/35px-Flag_of_Saint_Vincent_and_the_Grenadines.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Flag_of_Saint_Vincent_and_the_Grenadines.svg/45px-Flag_of_Saint_Vincent_and_the_Grenadines.svg.png 2x" data-file-width="450" data-file-height="300">&nbsp;</span>Saint Vincent and the Grenadines
</td>
<td>5 years
</td>
<td><a href="/wiki/2015_Vincentian_general_election" title="2015 Vincentian general election"><span data-sort-value="000000002015-12-09-0000" style="white-space:nowrap">9 December 2015</span></a>
</td>
<td><span data-sort-value="000000002020-12-01-0000" style="white-space:nowrap">December 2020</span>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>no data
</td>
<td><a href="/wiki/Unity_Labour_Party" title="Unity Labour Party">Unity Labour Party</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/6/60/Flag_of_Suriname.svg/23px-Flag_of_Suriname.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/6/60/Flag_of_Suriname.svg/35px-Flag_of_Suriname.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/6/60/Flag_of_Suriname.svg/45px-Flag_of_Suriname.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Suriname
</td>
<td>5 years
</td>
<td><a href="/wiki/2015_Surinamese_general_election" title="2015 Surinamese general election"><span data-sort-value="000000002015-05-25-0000" style="white-space:nowrap">25 May 2015</span></a>
</td>
<td><span data-sort-value="000000002020-05-01-0000" style="white-space:nowrap">May 2020</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>.526
</td>
<td><a href="/wiki/National_Democratic_Party_(Suriname)" title="National Democratic Party (Suriname)">National Democratic Party</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/6/64/Flag_of_Trinidad_and_Tobago.svg/23px-Flag_of_Trinidad_and_Tobago.svg.png" decoding="async" width="23" height="14" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/6/64/Flag_of_Trinidad_and_Tobago.svg/35px-Flag_of_Trinidad_and_Tobago.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/6/64/Flag_of_Trinidad_and_Tobago.svg/46px-Flag_of_Trinidad_and_Tobago.svg.png 2x" data-file-width="800" data-file-height="480">&nbsp;</span>Trinidad and Tobago
</td>
<td>5 years
</td>
<td><a href="/wiki/2015_Trinidad_and_Tobago_general_election" title="2015 Trinidad and Tobago general election"><span data-sort-value="000000002015-09-07-0000" style="white-space:nowrap">7 September 2015</span></a>
</td>
<td><a href="/wiki/2020_Trinidad_and_Tobago_general_election" title="2020 Trinidad and Tobago general election"><span data-sort-value="000000002020-09-01-0000" style="white-space:nowrap">September 2020</span></a>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>Very Fair<sup class="noprint Inline-Template Template-Fact" style="white-space:nowrap;">[<i><a href="/wiki/Wikipedia:Citation_needed" title="Wikipedia:Citation needed"><span title="Reliable source needed (December 2017)">citation needed</span></a></i>]</sup>
</td>
<td>1.3
</td>
<td>43.4
</td>
<td>.640
</td>
<td><a href="/wiki/People%27s_National_Movement" title="People's National Movement">People's National Movement</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/en/thumb/a/a4/Flag_of_the_United_States.svg/23px-Flag_of_the_United_States.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/en/thumb/a/a4/Flag_of_the_United_States.svg/35px-Flag_of_the_United_States.svg.png 1.5x, //upload.wikimedia.org/wikipedia/en/thumb/a/a4/Flag_of_the_United_States.svg/46px-Flag_of_the_United_States.svg.png 2x" data-file-width="1235" data-file-height="650">&nbsp;</span>United States
</td>
<td>2 years<sup id="cite_ref-US_Constitution_13-0" class="reference"><a href="#cite_note-US_Constitution-13">[13]</a></sup>
</td>
<td><a href="/w/index.php?title=2018_United_States_general_election&amp;action=edit&amp;redlink=1" class="new" title="2018 United States general election (page does not exist)"><span data-sort-value="000000002018-11-06-0000" style="white-space:nowrap">6 November 2018</span></a>
</td>
<td><a href="/wiki/2020_United_States_House_of_Representatives_elections" title="2020 United States House of Representatives elections"><span data-sort-value="000000002020-11-01-0000" style="white-space:nowrap">November 2020</span></a>
</td>
<td>4 years<sup id="cite_ref-US_Constitution_13-1" class="reference"><a href="#cite_note-US_Constitution-13">[13]</a></sup>
</td>
<td><a href="/wiki/2016_United_States_presidential_election" title="2016 United States presidential election"><span data-sort-value="000000002016-11-08-0000" style="white-space:nowrap">8 November 2016</span></a>
</td>
<td><a href="/wiki/2020_United_States_presidential_election" title="2020 United States presidential election"><span data-sort-value="000000002020-11-01-0000" style="white-space:nowrap">November 2020</span></a>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_the_United_States" class="mw-redirect" title="Demographics of the United States">316.4</a>
</td>
<td><a href="/wiki/Economy_of_the_United_States" title="Economy of the United States">14,991</a>
</td>
<td>.821
</td>
<td><a href="/wiki/Republican_Party_(United_States)" title="Republican Party (United States)">Republican</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/f/fe/Flag_of_Uruguay.svg/23px-Flag_of_Uruguay.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/f/fe/Flag_of_Uruguay.svg/35px-Flag_of_Uruguay.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/f/fe/Flag_of_Uruguay.svg/45px-Flag_of_Uruguay.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Uruguay
</td>
<td>5 years
</td>
<td><a href="/wiki/2014_Uruguayan_general_election" title="2014 Uruguayan general election"><span data-sort-value="000000002014-10-26-0000" style="white-space:nowrap">26 October 2014</span></a>
</td>
<td><a href="/wiki/2019_Uruguayan_general_election" title="2019 Uruguayan general election"><span data-sort-value="000000002019-10-27-0000" style="white-space:nowrap">27 October 2019</span></a>
</td>
<td>5 years
</td>
<td><a href="/wiki/2014_Uruguayan_general_election" title="2014 Uruguayan general election"><span data-sort-value="000000002014-10-26-0000" style="white-space:nowrap">26 October 2014</span></a>
</td>
<td><a href="/wiki/2019_Uruguayan_general_election" title="2019 Uruguayan general election"><span data-sort-value="000000002019-10-27-0000" style="white-space:nowrap">27 October 2019</span></a>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Uruguay" title="Demographics of Uruguay">3.3</a>
</td>
<td><a href="/wiki/Economy_of_Uruguay" title="Economy of Uruguay">46</a>
</td>
<td>.662
</td>
<td><a href="/wiki/Broad_Front_(Uruguay)" title="Broad Front (Uruguay)">Broad Front</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/0/06/Flag_of_Venezuela.svg/23px-Flag_of_Venezuela.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/0/06/Flag_of_Venezuela.svg/35px-Flag_of_Venezuela.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/0/06/Flag_of_Venezuela.svg/45px-Flag_of_Venezuela.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Venezuela
</td>
<td>5 years
</td>
<td><a href="/wiki/2015_Venezuelan_parliamentary_election" title="2015 Venezuelan parliamentary election"><span data-sort-value="000000002015-12-06-0000" style="white-space:nowrap">6 December 2015</span></a>
</td>
<td><span data-sort-value="000000002020-12-01-0000" style="white-space:nowrap">December 2020</span>
</td>
<td>6 years
</td>
<td><a href="/wiki/2018_Venezuelan_presidential_election" title="2018 Venezuelan presidential election"><span data-sort-value="000000002018-05-20-0000" style="white-space:nowrap">20 May 2018</span></a>
</td>
<td><span data-sort-value="000000002024-01-01-0000" style="white-space:nowrap">2024</span>
</td>
<td>Political suppression
</td>
<td><a href="/wiki/Demographics_of_Venezuela" title="Demographics of Venezuela">28.9</a>
</td>
<td><a href="/wiki/Economy_of_Venezuela" title="Economy of Venezuela">315</a>
</td>
<td>.549
</td>
<td><a href="/wiki/United_Socialist_Party_of_Venezuela" title="United Socialist Party of Venezuela">United Socialist</a>
</td></tr></tbody><tfoot></tfoot></table>
<table class="wikitable sortable jquery-tablesorter" style="font-size:90%;">
<thead><tr>
<th rowspan="2" class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">Country
</th>
<th colspan="3">Parliamentary election
</th>
<th colspan="3">Presidential election
</th>
<th rowspan="2" class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending"><a href="/wiki/Unfair_election" title="Unfair election">Fairness</a>
</th>
<th rowspan="2" class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending"><a href="/wiki/List_of_countries_by_population" class="mw-redirect" title="List of countries by population">Pop.</a><br>(m)
</th>
<th rowspan="2" class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending"><a href="/wiki/List_of_countries_by_GDP_(nominal)" title="List of countries by GDP (nominal)">GDP</a><br>($bn)
</th>
<th rowspan="2" class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending"><a href="/wiki/List_of_countries_by_inequality-adjusted_HDI" title="List of countries by inequality-adjusted HDI">IHDI</a>
</th>
<th rowspan="2" class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">In power now
</th></tr><tr>
<th class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">Term
</th>
<th class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">Last election
</th>
<th class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">Next election
</th>
<th class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">Term
</th>
<th class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">Last election
</th>
<th class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">Next election
</th></tr></thead><tbody>

<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Flag_of_Afghanistan.svg/23px-Flag_of_Afghanistan.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Flag_of_Afghanistan.svg/35px-Flag_of_Afghanistan.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Flag_of_Afghanistan.svg/45px-Flag_of_Afghanistan.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Afghanistan
</td>
<td>5 years
</td>
<td><a href="/wiki/2018_Afghan_parliamentary_election" title="2018 Afghan parliamentary election"><span data-sort-value="000000002018-10-20-0000" style="white-space:nowrap">20 October 2018</span></a>
</td>
<td><span data-sort-value="000000002023-01-01-0000" style="white-space:nowrap">2023</span>
</td>
<td>5 years
</td>
<td><a href="/wiki/2014_Afghan_presidential_election" title="2014 Afghan presidential election"><span data-sort-value="000000002014-04-05-0000" style="white-space:nowrap">5 April 2014</span></a>
</td>
<td><a href="/wiki/2019_Afghan_presidential_election" title="2019 Afghan presidential election"><span data-sort-value="000000002019-09-28-0000" style="white-space:nowrap">28 September 2019</span></a>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>no data
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Flag_of_Bahrain.svg/23px-Flag_of_Bahrain.svg.png" decoding="async" width="23" height="14" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Flag_of_Bahrain.svg/35px-Flag_of_Bahrain.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Flag_of_Bahrain.svg/46px-Flag_of_Bahrain.svg.png 2x" data-file-width="1500" data-file-height="900">&nbsp;</span>Bahrain
</td>
<td>4 years
</td>
<td><a href="/wiki/2014_Bahraini_general_election" title="2014 Bahraini general election"><span data-sort-value="000000002018-11-22-0000" style="white-space:nowrap">22 November 2018</span></a>
</td>
<td><span data-sort-value="000000002022-11-01-0000" style="white-space:nowrap">November 2022</span>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>no data
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Flag_of_Bangladesh.svg/23px-Flag_of_Bangladesh.svg.png" decoding="async" width="23" height="14" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Flag_of_Bangladesh.svg/35px-Flag_of_Bangladesh.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Flag_of_Bangladesh.svg/46px-Flag_of_Bangladesh.svg.png 2x" data-file-width="1000" data-file-height="600">&nbsp;</span>Bangladesh
</td>
<td>5 years
</td>
<td><a href="/wiki/2018_Bangladeshi_general_election" title="2018 Bangladeshi general election"><span data-sort-value="000000002018-12-30-0000" style="white-space:nowrap">30 December 2018</span></a>
</td>
<td><span data-sort-value="000000002023-12-01-0000" style="white-space:nowrap">December 2023</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Bangladesh" title="Demographics of Bangladesh">150.1</a>
</td>
<td><a href="/wiki/Economy_of_Bangladesh" title="Economy of Bangladesh">122</a>
</td>
<td>.374
</td>
<td><a href="/wiki/Bangladesh_Awami_League" class="mw-redirect" title="Bangladesh Awami League">Awami League</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/9/91/Flag_of_Bhutan.svg/23px-Flag_of_Bhutan.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/9/91/Flag_of_Bhutan.svg/35px-Flag_of_Bhutan.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/9/91/Flag_of_Bhutan.svg/45px-Flag_of_Bhutan.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Bhutan
</td>
<td>5 years
</td>
<td><a href="/wiki/2018_Bhutanese_National_Assembly_election" title="2018 Bhutanese National Assembly election"><span data-sort-value="000000002018-09-15-0000" style="white-space:nowrap">15 September 2018</span></a>
</td>
<td><span data-sort-value="000000002023-09-01-0000" style="white-space:nowrap">September 2023</span>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>.430
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Flag_of_Myanmar.svg/23px-Flag_of_Myanmar.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Flag_of_Myanmar.svg/35px-Flag_of_Myanmar.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Flag_of_Myanmar.svg/45px-Flag_of_Myanmar.svg.png 2x" data-file-width="1200" data-file-height="800">&nbsp;</span>Burma
</td>
<td>5 years
</td>
<td><a href="/wiki/2015_Myanmar_general_election" title="2015 Myanmar general election"><span data-sort-value="000000002015-11-08-0000" style="white-space:nowrap">8 November 2015</span></a>
</td>
<td><span data-sort-value="000000002020-11-01-0000" style="white-space:nowrap">November 2020</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>no data
</td>
<td><a href="/wiki/National_League_for_Democracy" title="National League for Democracy">National League for Democracy</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/8/83/Flag_of_Cambodia.svg/23px-Flag_of_Cambodia.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/8/83/Flag_of_Cambodia.svg/35px-Flag_of_Cambodia.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/8/83/Flag_of_Cambodia.svg/46px-Flag_of_Cambodia.svg.png 2x" data-file-width="625" data-file-height="400">&nbsp;</span>Cambodia
</td>
<td>5 years
</td>
<td><a href="/wiki/2018_Cambodian_general_election" title="2018 Cambodian general election"><span data-sort-value="000000002018-07-29-0000" style="white-space:nowrap">29 July 2018</span></a>
</td>
<td><span data-sort-value="000000002023-07-01-0000" style="white-space:nowrap">July 2023</span>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>.402
</td>
<td><a href="/wiki/Cambodian_People%27s_Party" title="Cambodian People's Party">Cambodian People's Party</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Flag_of_Hong_Kong.svg/23px-Flag_of_Hong_Kong.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Flag_of_Hong_Kong.svg/35px-Flag_of_Hong_Kong.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Flag_of_Hong_Kong.svg/45px-Flag_of_Hong_Kong.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Hong Kong
</td>
<td>4 years
</td>
<td><a href="/wiki/2016_Hong_Kong_legislative_election" title="2016 Hong Kong legislative election"><span data-sort-value="000000002016-09-04-0000" style="white-space:nowrap">4 September 2016</span></a>
</td>
<td><a href="/wiki/2020_Hong_Kong_legislative_election" title="2020 Hong Kong legislative election"><span data-sort-value="000000002020-09-01-0000" style="white-space:nowrap">September 2020</span></a>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Hong_Kong" title="Demographics of Hong Kong">7.1</a>
</td>
<td><a href="/wiki/Economy_of_Hong_Kong" title="Economy of Hong Kong">243</a>
</td>
<td>no data
</td>
<td><a href="/wiki/Pro-Beijing_camp" class="mw-redirect" title="Pro-Beijing camp">Pro-Beijing camp</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/en/thumb/4/41/Flag_of_India.svg/23px-Flag_of_India.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/en/thumb/4/41/Flag_of_India.svg/35px-Flag_of_India.svg.png 1.5x, //upload.wikimedia.org/wikipedia/en/thumb/4/41/Flag_of_India.svg/45px-Flag_of_India.svg.png 2x" data-file-width="1350" data-file-height="900">&nbsp;</span>India
</td>
<td>5 years<sup id="cite_ref-14" class="reference"><a href="#cite_note-14">[14]</a></sup>
</td>
<td><a href="/wiki/2019_Indian_general_election" title="2019 Indian general election"><span data-sort-value="000000002019-04-11-0000" style="white-space:nowrap">11 April 2019</span></a>
</td>
<td><span data-sort-value="000000002024-04-01-0000" style="white-space:nowrap">April 2024</span>
</td>
<td>5 years
</td>
<td><a href="/wiki/2017_Indian_presidential_election" title="2017 Indian presidential election"><span data-sort-value="000000002017-07-17-0000" style="white-space:nowrap">17 July 2017</span></a>
</td>
<td><span data-sort-value="000000002022-07-01-0000" style="white-space:nowrap">July 2022</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>.392
</td>
<td><a href="/wiki/Bharatiya_Janata_Party" title="Bharatiya Janata Party">BJP</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Flag_of_Indonesia.svg/23px-Flag_of_Indonesia.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Flag_of_Indonesia.svg/35px-Flag_of_Indonesia.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Flag_of_Indonesia.svg/45px-Flag_of_Indonesia.svg.png 2x" data-file-width="450" data-file-height="300">&nbsp;</span>Indonesia
</td>
<td>5 years
</td>
<td><a href="/wiki/2019_Indonesian_legislative_election" class="mw-redirect" title="2019 Indonesian legislative election"><span data-sort-value="000000002019-04-17-0000" style="white-space:nowrap">17 April 2019</span></a>
</td>
<td><span data-sort-value="000000002024-04-01-0000" style="white-space:nowrap">April 2024</span>
</td>
<td>5 years
</td>
<td><a href="/wiki/2019_Indonesian_presidential_election" class="mw-redirect" title="2019 Indonesian presidential election"><span data-sort-value="000000002019-04-17-0000" style="white-space:nowrap">17 April 2019</span></a>
</td>
<td><span data-sort-value="000000002024-04-01-0000" style="white-space:nowrap">April 2024</span>
</td>
<td><a href="/wiki/2009_Indonesian_legislative_election#Controversies" title="2009 Indonesian legislative election">Voter suppression</a>
</td>
<td><a href="/wiki/Demographics_of_Indonesia" title="Demographics of Indonesia">237</a>
</td>
<td><a href="/wiki/Economy_of_Indonesia" title="Economy of Indonesia">946</a>
</td>
<td>.514
</td>
<td><a href="/wiki/Indonesian_Democratic_Party_-_Struggle" class="mw-redirect" title="Indonesian Democratic Party - Struggle">PDI-P</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/c/ca/Flag_of_Iran.svg/23px-Flag_of_Iran.svg.png" decoding="async" width="23" height="13" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/c/ca/Flag_of_Iran.svg/35px-Flag_of_Iran.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/c/ca/Flag_of_Iran.svg/46px-Flag_of_Iran.svg.png 2x" data-file-width="630" data-file-height="360">&nbsp;</span>Iran
</td>
<td>4 years
</td>
<td><a href="/wiki/2016_Iranian_legislative_election" title="2016 Iranian legislative election"><span data-sort-value="000000002016-02-26-0000" style="white-space:nowrap">26 February 2016</span></a>
</td>
<td><a href="/w/index.php?title=2020_Iranian_legislative_election&amp;action=edit&amp;redlink=1" class="new" title="2020 Iranian legislative election (page does not exist)"><span data-sort-value="000000002020-02-01-0000" style="white-space:nowrap">February 2020</span></a>
</td>
<td>4 years
</td>
<td><a href="/wiki/2017_Iranian_presidential_election" title="2017 Iranian presidential election"><span data-sort-value="000000002017-05-19-0000" style="white-space:nowrap">19 May 2017</span></a>
</td>
<td><a href="/wiki/2021_Iranian_presidential_election" title="2021 Iranian presidential election"><span data-sort-value="000000002021-01-01-0000" style="white-space:nowrap">2021</span></a>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Iran" title="Demographics of Iran">77.3</a>
</td>
<td><a href="/wiki/Economy_of_Iran" title="Economy of Iran">551</a>
</td>
<td>no data
</td>
<td><a href="/wiki/Iranian_reform_movement" class="mw-redirect" title="Iranian reform movement">Reformists</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Flag_of_Iraq.svg/23px-Flag_of_Iraq.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Flag_of_Iraq.svg/35px-Flag_of_Iraq.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Flag_of_Iraq.svg/45px-Flag_of_Iraq.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Iraq
</td>
<td>4 years
</td>
<td><a href="/wiki/2018_Iraqi_parliamentary_election" title="2018 Iraqi parliamentary election"><span data-sort-value="000000002018-05-12-0000" style="white-space:nowrap">12 May 2018</span></a>
</td>
<td><a href="/w/index.php?title=2022_Iraqi_parliamentary_election&amp;action=edit&amp;redlink=1" class="new" title="2022 Iraqi parliamentary election (page does not exist)"><span data-sort-value="000000002022-05-01-0000" style="white-space:nowrap">May 2022</span></a>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/Iraqi_Civil_War_(2014%E2%80%932017)" title="Iraqi Civil War (2014–2017)">Civil War</a>
</td>
<td><a href="/wiki/Demographics_of_Iraq" title="Demographics of Iraq">31.1</a>
</td>
<td><a href="/wiki/Economy_of_Iraq" title="Economy of Iraq">150</a>
</td>
<td>no data
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Flag_of_Israel.svg/21px-Flag_of_Israel.svg.png" decoding="async" width="21" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Flag_of_Israel.svg/32px-Flag_of_Israel.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Flag_of_Israel.svg/41px-Flag_of_Israel.svg.png 2x" data-file-width="660" data-file-height="480">&nbsp;</span>Israel
</td>
<td>4 years
</td>
<td><a href="/wiki/April_2019_Israeli_legislative_election" title="April 2019 Israeli legislative election"><span data-sort-value="000000002019-04-09-0000" style="white-space:nowrap">9 April 2019</span></a>
</td>
<td><a href="/wiki/September_2019_Israeli_legislative_election" title="September 2019 Israeli legislative election"><span data-sort-value="000000002019-09-17-0000" style="white-space:nowrap">17 September 2019</span></a>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Israel" title="Demographics of Israel">8.7</a>
</td>
<td><a href="/wiki/Economy_of_Israel" title="Economy of Israel">300</a>
</td>
<td>.778<sup id="cite_ref-15" class="reference"><a href="#cite_note-15">[15]</a></sup>
</td>
<td>Coalition: <a href="/wiki/Likud" title="Likud">Likud</a>, <a href="/wiki/Kulanu" title="Kulanu">Kulanu</a>,<br><a href="/wiki/The_Jewish_Home" title="The Jewish Home">The Jewish Home</a>,<br><a href="/wiki/United_Torah_Judaism" title="United Torah Judaism">United Torah Judaism</a>,<br><a href="/wiki/Shas" title="Shas">Shas</a>, <a href="/wiki/Yisrael_Beitenu" class="mw-redirect" title="Yisrael Beitenu">Yisrael Beitenu</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/en/thumb/9/9e/Flag_of_Japan.svg/23px-Flag_of_Japan.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/en/thumb/9/9e/Flag_of_Japan.svg/35px-Flag_of_Japan.svg.png 1.5x, //upload.wikimedia.org/wikipedia/en/thumb/9/9e/Flag_of_Japan.svg/45px-Flag_of_Japan.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Japan
</td>
<td>4 years
</td>
<td><a href="/wiki/48th_Japanese_general_election" class="mw-redirect" title="48th Japanese general election"><span data-sort-value="000000002017-10-22-0000" style="white-space:nowrap">22 October 2017</span></a>
</td>
<td><a href="/wiki/Next_Japanese_general_election" title="Next Japanese general election"><span data-sort-value="000000002021-10-01-0000" style="white-space:nowrap">October 2021</span></a>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Japan" title="Demographics of Japan">126.6</a>
</td>
<td><a href="/wiki/Economy_of_Japan" title="Economy of Japan">5,150</a>
</td>
<td>no data
</td>
<td><a href="/wiki/Liberal_Democratic_Party_(Japan)" title="Liberal Democratic Party (Japan)">Liberal Democratic</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/c/c0/Flag_of_Jordan.svg/23px-Flag_of_Jordan.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/c/c0/Flag_of_Jordan.svg/35px-Flag_of_Jordan.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/c/c0/Flag_of_Jordan.svg/46px-Flag_of_Jordan.svg.png 2x" data-file-width="1000" data-file-height="500">&nbsp;</span>Jordan
</td>
<td>4 years
</td>
<td><a href="/wiki/2016_Jordanian_general_election" title="2016 Jordanian general election"><span data-sort-value="000000002016-09-20-0000" style="white-space:nowrap">20 September 2016</span></a>
</td>
<td><span data-sort-value="000000002020-09-01-0000" style="white-space:nowrap">September 2020</span>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>.568
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Flag_of_Kazakhstan.svg/23px-Flag_of_Kazakhstan.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Flag_of_Kazakhstan.svg/35px-Flag_of_Kazakhstan.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Flag_of_Kazakhstan.svg/46px-Flag_of_Kazakhstan.svg.png 2x" data-file-width="600" data-file-height="300">&nbsp;</span>Kazakhstan
</td>
<td>4 years
</td>
<td><a href="/wiki/2016_Kazakhstani_legislative_election" class="mw-redirect" title="2016 Kazakhstani legislative election"><span data-sort-value="000000002016-03-20-0000" style="white-space:nowrap">20 March 2016</span></a>
</td>
<td><span data-sort-value="000000002020-03-01-0000" style="white-space:nowrap">March 2020</span>
</td>
<td>
</td>
<td><a href="/wiki/2015_Kazakhstani_presidential_election" class="mw-redirect" title="2015 Kazakhstani presidential election"><span data-sort-value="000000002015-04-26-0000" style="white-space:nowrap">26 April 2015</span></a>
</td>
<td><span data-sort-value="000000002020-01-01-0000" style="white-space:nowrap">2020</span>
</td>
<td>
</td>
<td>
</td>
<td>no data
</td>
<td>
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/a/aa/Flag_of_Kuwait.svg/23px-Flag_of_Kuwait.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/a/aa/Flag_of_Kuwait.svg/35px-Flag_of_Kuwait.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/a/aa/Flag_of_Kuwait.svg/46px-Flag_of_Kuwait.svg.png 2x" data-file-width="1200" data-file-height="600">&nbsp;</span>Kuwait
</td>
<td>4 years
</td>
<td><a href="/wiki/2016_Kuwaiti_general_election" title="2016 Kuwaiti general election"><span data-sort-value="000000002016-11-26-0000" style="white-space:nowrap">26 November 2016</span></a>
</td>
<td><span data-sort-value="000000002020-10-01-0000" style="white-space:nowrap">October 2020</span>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>no data
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Flag_of_Kyrgyzstan.svg/23px-Flag_of_Kyrgyzstan.svg.png" decoding="async" width="23" height="14" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Flag_of_Kyrgyzstan.svg/35px-Flag_of_Kyrgyzstan.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Flag_of_Kyrgyzstan.svg/46px-Flag_of_Kyrgyzstan.svg.png 2x" data-file-width="1000" data-file-height="600">&nbsp;</span>Kyrgyzstan
</td>
<td>5 years
</td>
<td><a href="/wiki/2015_Kyrgyzstani_parliamentary_election" class="mw-redirect" title="2015 Kyrgyzstani parliamentary election"><span data-sort-value="000000002015-10-04-0000" style="white-space:nowrap">4 October 2015</span></a>
</td>
<td><span data-sort-value="000000002020-10-01-0000" style="white-space:nowrap">October 2020</span>
</td>
<td>6 years
</td>
<td><a href="/w/index.php?title=2017_Kyrgyzstani_presidential_election&amp;action=edit&amp;redlink=1" class="new" title="2017 Kyrgyzstani presidential election (page does not exist)"><span data-sort-value="000000002017-10-15-0000" style="white-space:nowrap">15 October 2017</span></a>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>.516
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/5/56/Flag_of_Laos.svg/23px-Flag_of_Laos.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/5/56/Flag_of_Laos.svg/35px-Flag_of_Laos.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/5/56/Flag_of_Laos.svg/45px-Flag_of_Laos.svg.png 2x" data-file-width="600" data-file-height="400">&nbsp;</span>Laos
</td>
<td>5 years
</td>
<td><a href="/wiki/2016_Laotian_parliamentary_election" title="2016 Laotian parliamentary election"><span data-sort-value="000000002016-03-20-0000" style="white-space:nowrap">20 March 2016</span></a>
</td>
<td><span data-sort-value="000000002021-03-01-0000" style="white-space:nowrap">March 2021</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>.409
</td>
<td><a href="/wiki/Lao_People%27s_Revolutionary_Party" title="Lao People's Revolutionary Party">Lao People's Revolutionary Party</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/5/59/Flag_of_Lebanon.svg/23px-Flag_of_Lebanon.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/5/59/Flag_of_Lebanon.svg/35px-Flag_of_Lebanon.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/5/59/Flag_of_Lebanon.svg/45px-Flag_of_Lebanon.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Lebanon
</td>
<td>4 years
</td>
<td><a href="/wiki/2018_Lebanese_general_election" title="2018 Lebanese general election"><span data-sort-value="000000002018-05-06-0000" style="white-space:nowrap">6 May 2018</span></a>
</td>
<td><span data-sort-value="000000002022-05-01-0000" style="white-space:nowrap">May 2022</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>.575
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/6/66/Flag_of_Malaysia.svg/23px-Flag_of_Malaysia.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/6/66/Flag_of_Malaysia.svg/35px-Flag_of_Malaysia.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/6/66/Flag_of_Malaysia.svg/46px-Flag_of_Malaysia.svg.png 2x" data-file-width="2800" data-file-height="1400">&nbsp;</span>Malaysia
</td>
<td>5 years
</td>
<td><a href="/wiki/2018_Malaysian_general_election" title="2018 Malaysian general election"><span data-sort-value="000000002018-05-09-0000" style="white-space:nowrap">9 May 2018</span></a>
</td>
<td><a href="/wiki/Next_Malaysian_general_election" class="mw-redirect" title="Next Malaysian general election"><span data-sort-value="000000002023-05-01-0000" style="white-space:nowrap">May 2023</span></a>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td><a href="/wiki/2013_Malaysian_general_election#Reactions.2C_analysis_and_aftermath" title="2013 Malaysian general election">Alleged fraud</a>
</td>
<td><a href="/wiki/Demographics_of_Malaysia" title="Demographics of Malaysia">28.3</a>
</td>
<td><a href="/wiki/Economy_of_Malaysia" title="Economy of Malaysia">240</a>
</td>
<td>no data
</td>
<td><a href="/wiki/Pakatan_Harapan" title="Pakatan Harapan">Pakatan Harapan</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Flag_of_Maldives.svg/23px-Flag_of_Maldives.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Flag_of_Maldives.svg/35px-Flag_of_Maldives.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Flag_of_Maldives.svg/45px-Flag_of_Maldives.svg.png 2x" data-file-width="720" data-file-height="480">&nbsp;</span>Maldives
</td>
<td>5 years
</td>
<td><a href="/wiki/2019_Maldivian_parliamentary_election" title="2019 Maldivian parliamentary election"><span data-sort-value="000000002019-04-06-0000" style="white-space:nowrap">6 April 2019</span></a>
</td>
<td><span data-sort-value="000000002024-04-01-0000" style="white-space:nowrap">April 2024</span>
</td>
<td>5 years
</td>
<td><a href="/wiki/2018_Maldivian_presidential_election" title="2018 Maldivian presidential election"><span data-sort-value="000000002018-09-23-0000" style="white-space:nowrap">23 September 2018</span></a>
</td>
<td><span data-sort-value="000000002023-01-01-0000" style="white-space:nowrap">2023</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>.515
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Flag_of_Mongolia.svg/23px-Flag_of_Mongolia.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Flag_of_Mongolia.svg/35px-Flag_of_Mongolia.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Flag_of_Mongolia.svg/46px-Flag_of_Mongolia.svg.png 2x" data-file-width="4800" data-file-height="2400">&nbsp;</span>Mongolia
</td>
<td>4 years
</td>
<td><a href="/wiki/2016_Mongolian_legislative_election" title="2016 Mongolian legislative election"><span data-sort-value="000000002016-06-29-0000" style="white-space:nowrap">29 June 2016</span></a>
</td>
<td><span data-sort-value="000000002020-06-01-0000" style="white-space:nowrap">June 2020</span>
</td>
<td>4 years
</td>
<td><a href="/wiki/2017_Mongolian_presidential_election" title="2017 Mongolian presidential election"><span data-sort-value="000000002017-06-26-0000" style="white-space:nowrap">26 June 2017</span></a>
</td>
<td><span data-sort-value="000000002021-06-01-0000" style="white-space:nowrap">June 2021</span>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Mongolia" title="Demographics of Mongolia">2.8</a>
</td>
<td><a href="/wiki/Economy_of_Mongolia" title="Economy of Mongolia">10</a>
</td>
<td>.568
</td>
<td><a href="/wiki/Democratic_Party_(Mongolia)" title="Democratic Party (Mongolia)">Democrats</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Flag_of_Nepal.svg/16px-Flag_of_Nepal.svg.png" decoding="async" width="16" height="20" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Flag_of_Nepal.svg/25px-Flag_of_Nepal.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Flag_of_Nepal.svg/33px-Flag_of_Nepal.svg.png 2x" data-file-width="726" data-file-height="885">&nbsp;&nbsp;&nbsp;</span>Nepal
</td>
<td>5 years
</td>
<td><a href="/wiki/2017_Nepalese_legislative_election" title="2017 Nepalese legislative election"><span data-sort-value="000000002017-11-26-0000" style="white-space:nowrap">26 November 2017</span></a>
</td>
<td><span data-sort-value="000000002022-11-01-0000" style="white-space:nowrap">November 2022</span>
</td>
<td>5 years
</td>
<td><a href="/wiki/2018_Nepalese_presidential_election" title="2018 Nepalese presidential election"><span data-sort-value="000000002018-03-13-0000" style="white-space:nowrap">13 March 2018</span></a>
</td>
<td><span data-sort-value="000000002023-03-01-0000" style="white-space:nowrap">March 2023</span>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Nepal" title="Demographics of Nepal">26.5</a>
</td>
<td><a href="/wiki/Economy_of_Nepal" title="Economy of Nepal">20</a>
</td>
<td>.304
</td>
<td><a href="/wiki/Unified_Communist_Party_of_Nepal_(Maoist)" class="mw-redirect" title="Unified Communist Party of Nepal (Maoist)">Communist</a>/Coal.
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/5/51/Flag_of_North_Korea.svg/23px-Flag_of_North_Korea.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/5/51/Flag_of_North_Korea.svg/35px-Flag_of_North_Korea.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/5/51/Flag_of_North_Korea.svg/46px-Flag_of_North_Korea.svg.png 2x" data-file-width="1600" data-file-height="800">&nbsp;</span>North Korea
</td>
<td>5 years
</td>
<td><a href="/wiki/2019_North_Korean_parliamentary_election" title="2019 North Korean parliamentary election"><span data-sort-value="000000002019-03-10-0000" style="white-space:nowrap">10 March 2019</span></a>
</td>
<td><span data-sort-value="000000002024-01-01-0000" style="white-space:nowrap">2024</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>One candidate per seat,<br>chosen by the governing party.<br>No democratic choice.<br>Widespread intimidation.
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/Workers%27_Party_of_Korea" title="Workers' Party of Korea">WPK</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Flag_of_Oman.svg/23px-Flag_of_Oman.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Flag_of_Oman.svg/35px-Flag_of_Oman.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Flag_of_Oman.svg/46px-Flag_of_Oman.svg.png 2x" data-file-width="600" data-file-height="300">&nbsp;</span>Oman
</td>
<td>4 years
</td>
<td><a href="/wiki/2015_Omani_general_election" title="2015 Omani general election"><span data-sort-value="000000002015-10-25-0000" style="white-space:nowrap">25 October 2015</span></a>
</td>
<td><a href="/wiki/2015_Omani_general_election" title="2015 Omani general election"><span data-sort-value="000000002019-10-01-0000" style="white-space:nowrap">October 2019</span></a>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>Absolute monarchy.<br>Elections to a Consultative Assembly only.<br>Political parties are prohibited.
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>(no political parties;<br>no <a href="/wiki/Responsible_government" title="Responsible government">responsible government</a>)
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/3/32/Flag_of_Pakistan.svg/23px-Flag_of_Pakistan.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/3/32/Flag_of_Pakistan.svg/35px-Flag_of_Pakistan.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/3/32/Flag_of_Pakistan.svg/45px-Flag_of_Pakistan.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Pakistan
</td>
<td>5 years
</td>
<td><a href="/w/index.php?title=2018_Pakistan_general_election&amp;action=edit&amp;redlink=1" class="new" title="2018 Pakistan general election (page does not exist)"><span data-sort-value="000000002018-07-25-0000" style="white-space:nowrap">25 July 2018</span></a>
</td>
<td><span data-sort-value="000000002023-07-01-0000" style="white-space:nowrap">July 2023</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/2018_Pakistani_general_election#Conduct" title="2018 Pakistani general election">Violence, alleged tampering</a>
</td>
<td><a href="/wiki/Demographics_of_Pakistan" title="Demographics of Pakistan">182.5</a>
</td>
<td><a href="/wiki/Economy_of_Pakistan" title="Economy of Pakistan">230</a>
</td>
<td>.356
</td>
<td><a href="/wiki/Pakistan_Tehreek-e-Insaf" title="Pakistan Tehreek-e-Insaf">Pakistan Tehreek-e-Insaf</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/0/00/Flag_of_Palestine.svg/23px-Flag_of_Palestine.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/0/00/Flag_of_Palestine.svg/35px-Flag_of_Palestine.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/0/00/Flag_of_Palestine.svg/46px-Flag_of_Palestine.svg.png 2x" data-file-width="1200" data-file-height="600">&nbsp;</span>Palestinian Territory
</td>
<td>
</td>
<td><a href="/wiki/2006_Palestinian_legislative_election" title="2006 Palestinian legislative election"><span data-sort-value="000000002006-01-25-0000" style="white-space:nowrap">25 January 2006</span></a>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/2005_Palestinian_presidential_election" title="2005 Palestinian presidential election">9 January 2005</a>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>no data
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/9/99/Flag_of_the_Philippines.svg/23px-Flag_of_the_Philippines.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/9/99/Flag_of_the_Philippines.svg/35px-Flag_of_the_Philippines.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/9/99/Flag_of_the_Philippines.svg/46px-Flag_of_the_Philippines.svg.png 2x" data-file-width="900" data-file-height="450">&nbsp;</span>Philippines
</td>
<td>3 years
</td>
<td><a href="/wiki/2019_Philippine_general_election" title="2019 Philippine general election"><span data-sort-value="000000002019-05-13-0000" style="white-space:nowrap">13 May 2019</span></a>
</td>
<td><a href="/wiki/2022_Philippine_presidential_election" title="2022 Philippine presidential election"><span data-sort-value="000000002022-05-01-0000" style="white-space:nowrap">May 2022</span></a>
</td>
<td>6 years
</td>
<td><a href="/wiki/2016_Philippine_general_election" title="2016 Philippine general election"><span data-sort-value="000000002016-05-09-0000" style="white-space:nowrap">9 May 2016</span></a>
</td>
<td><a href="/wiki/2022_Philippine_presidential_election" title="2022 Philippine presidential election"><span data-sort-value="000000002022-05-01-0000" style="white-space:nowrap">May 2022</span></a>
</td>
<td><a href="/wiki/Controversies_in_the_Philippine_general_election,_2010" class="mw-redirect" title="Controversies in the Philippine general election, 2010">Violence, voter suppression</a>
</td>
<td><a href="/wiki/Demographics_of_the_Philippines" title="Demographics of the Philippines">98.2</a>
</td>
<td><a href="/wiki/Economy_of_the_Philippines" title="Economy of the Philippines">284</a>
</td>
<td>.524
</td>
<td><a href="/wiki/Liberal_Party_(Philippines)" title="Liberal Party (Philippines)">Liberal</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/4/48/Flag_of_Singapore.svg/23px-Flag_of_Singapore.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/4/48/Flag_of_Singapore.svg/35px-Flag_of_Singapore.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/4/48/Flag_of_Singapore.svg/45px-Flag_of_Singapore.svg.png 2x" data-file-width="4320" data-file-height="2880">&nbsp;</span>Singapore
</td>
<td>5 years
</td>
<td><a href="/wiki/2015_Singaporean_general_election" title="2015 Singaporean general election"><span data-sort-value="000000002015-09-11-0000" style="white-space:nowrap">11 September 2015</span></a>
</td>
<td><a href="/wiki/Next_Singaporean_general_election" title="Next Singaporean general election"><span data-sort-value="000000002020-09-01-0000" style="white-space:nowrap">September 2020</span></a>
</td>
<td>6 years
</td>
<td><a href="/wiki/2017_Singaporean_presidential_election" title="2017 Singaporean presidential election"><span data-sort-value="000000002017-09-13-0000" style="white-space:nowrap">13 September 2017</span></a>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Singapore" title="Demographics of Singapore">5.3</a>
</td>
<td><a href="/wiki/Economy_of_Singapore" title="Economy of Singapore">270</a>
</td>
<td>no data
</td>
<td><a href="/wiki/People%27s_Action_Party" title="People's Action Party">PAP</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/0/09/Flag_of_South_Korea.svg/23px-Flag_of_South_Korea.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/0/09/Flag_of_South_Korea.svg/35px-Flag_of_South_Korea.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/0/09/Flag_of_South_Korea.svg/45px-Flag_of_South_Korea.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>South Korea
</td>
<td>4 years
</td>
<td><a href="/wiki/2016_South_Korean_legislative_election" title="2016 South Korean legislative election"><span data-sort-value="000000002016-04-13-0000" style="white-space:nowrap">13 April 2016</span></a>
</td>
<td><a href="/wiki/2020_South_Korean_legislative_election" title="2020 South Korean legislative election"><span data-sort-value="000000002020-04-01-0000" style="white-space:nowrap">April 2020</span></a>
</td>
<td>5 years
</td>
<td><a href="/wiki/2017_South_Korean_presidential_election" title="2017 South Korean presidential election"><span data-sort-value="000000002017-05-09-0000" style="white-space:nowrap">9 May 2017</span></a>
</td>
<td><span data-sort-value="000000002022-01-01-0000" style="white-space:nowrap">2022</span>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_South_Korea" title="Demographics of South Korea">50.0</a>
</td>
<td><a href="/wiki/Economy_of_South_Korea" title="Economy of South Korea">1,259</a>
</td>
<td>.758
</td>
<td><a href="/wiki/Democratic_Party_of_Korea" title="Democratic Party of Korea">Democratic Party of Korea</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/1/11/Flag_of_Sri_Lanka.svg/23px-Flag_of_Sri_Lanka.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/1/11/Flag_of_Sri_Lanka.svg/35px-Flag_of_Sri_Lanka.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/1/11/Flag_of_Sri_Lanka.svg/46px-Flag_of_Sri_Lanka.svg.png 2x" data-file-width="1200" data-file-height="600">&nbsp;</span>Sri Lanka
</td>
<td>6 years
</td>
<td><a href="/wiki/2015_Sri_Lankan_parliamentary_election" title="2015 Sri Lankan parliamentary election"><span data-sort-value="000000002015-08-17-0000" style="white-space:nowrap">17 August 2015</span></a>
</td>
<td><span data-sort-value="000000002021-08-01-0000" style="white-space:nowrap">August 2021</span>
</td>
<td>5 years
</td>
<td><a href="/wiki/2015_Sri_Lankan_presidential_election" title="2015 Sri Lankan presidential election"><span data-sort-value="000000002015-01-08-0000" style="white-space:nowrap">8 January 2015</span></a>
</td>
<td><a href="/w/index.php?title=2020_Sri_Lankan_presidential_election&amp;action=edit&amp;redlink=1" class="new" title="2020 Sri Lankan presidential election (page does not exist)"><span data-sort-value="000000002020-01-01-0000" style="white-space:nowrap">January 2020</span></a>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Sri_Lanka" title="Demographics of Sri Lanka">20.2</a>
</td>
<td><a href="/wiki/Economy_of_Sri_Lanka" title="Economy of Sri Lanka">65</a>
</td>
<td>.643
</td>
<td>National Unity Government (<a href="/wiki/United_National_Party" title="United National Party">UNP</a> and <a href="/wiki/United_People%27s_Freedom_Alliance" title="United People's Freedom Alliance">UPFA</a>)
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/5/53/Flag_of_Syria.svg/23px-Flag_of_Syria.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/5/53/Flag_of_Syria.svg/35px-Flag_of_Syria.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/5/53/Flag_of_Syria.svg/45px-Flag_of_Syria.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Syria
</td>
<td>4 years
</td>
<td><a href="/wiki/2016_Syrian_parliamentary_election" title="2016 Syrian parliamentary election"><span data-sort-value="000000002016-04-13-0000" style="white-space:nowrap">13 April 2016</span></a>
</td>
<td><span data-sort-value="000000002020-04-01-0000" style="white-space:nowrap">April 2020</span>
</td>
<td>7 years
</td>
<td><a href="/wiki/2014_Syrian_presidential_election" title="2014 Syrian presidential election"><span data-sort-value="000000002014-06-03-0000" style="white-space:nowrap">3 June 2014</span></a>
</td>
<td><span data-sort-value="000000002021-01-01-0000" style="white-space:nowrap">2021</span>
</td>
<td><a href="/wiki/Syrian_Civil_War" title="Syrian Civil War">Civil War</a>
</td>
<td>
</td>
<td>
</td>
<td>.515
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/7/72/Flag_of_the_Republic_of_China.svg/23px-Flag_of_the_Republic_of_China.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/7/72/Flag_of_the_Republic_of_China.svg/35px-Flag_of_the_Republic_of_China.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/7/72/Flag_of_the_Republic_of_China.svg/45px-Flag_of_the_Republic_of_China.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Taiwan
</td>
<td>4 years
</td>
<td><a href="/wiki/2016_Taiwan_general_election" title="2016 Taiwan general election">16 January 2016</a>
</td>
<td><a href="/wiki/2020_Taiwan_general_election" title="2020 Taiwan general election">January 2020</a>
</td>
<td>4 years
</td>
<td><a href="/wiki/2016_Taiwan_presidential_election" title="2016 Taiwan presidential election"><span data-sort-value="000000002016-01-16-0000" style="white-space:nowrap">16 January 2016</span></a>
</td>
<td><a href="/wiki/2020_Taiwan_presidential_election" title="2020 Taiwan presidential election"><span data-sort-value="000000002020-01-01-0000" style="white-space:nowrap">January 2020</span></a>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Taiwan" title="Demographics of Taiwan">23.3</a>
</td>
<td><a href="/wiki/Economy_of_Taiwan" title="Economy of Taiwan">473</a>
</td>
<td>no data
</td>
<td><a href="/wiki/Democratic_Progressive_Party" title="Democratic Progressive Party">DPP</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Flag_of_Tajikistan.svg/23px-Flag_of_Tajikistan.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Flag_of_Tajikistan.svg/35px-Flag_of_Tajikistan.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Flag_of_Tajikistan.svg/46px-Flag_of_Tajikistan.svg.png 2x" data-file-width="1200" data-file-height="600">&nbsp;</span>Tajikistan
</td>
<td>5 years
</td>
<td><a href="/wiki/2015_Tajikistani_parliamentary_election" class="mw-redirect" title="2015 Tajikistani parliamentary election"><span data-sort-value="000000002015-03-01-0000" style="white-space:nowrap">1 March 2015</span></a>
</td>
<td><span data-sort-value="000000002020-03-01-0000" style="white-space:nowrap">March 2020</span>
</td>
<td>7 years
</td>
<td><a href="/wiki/2013_Tajikistani_presidential_election" class="mw-redirect" title="2013 Tajikistani presidential election"><span data-sort-value="000000002013-11-06-0000" style="white-space:nowrap">6 November 2013</span></a>
</td>
<td><span data-sort-value="000000002020-01-01-0000" style="white-space:nowrap">2020</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>.507
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Flag_of_Thailand.svg/23px-Flag_of_Thailand.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Flag_of_Thailand.svg/35px-Flag_of_Thailand.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Flag_of_Thailand.svg/45px-Flag_of_Thailand.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Thailand
</td>
<td>4 years
</td>
<td><a href="/wiki/2019_Thai_general_election" title="2019 Thai general election"><span data-sort-value="000000002019-03-24-0000" style="white-space:nowrap">24 March 2019</span></a>
</td>
<td><span data-sort-value="000000002023-03-01-0000" style="white-space:nowrap">March 2023</span>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>Military interference
</td>
<td><a href="/wiki/Demographics_of_Thailand" title="Demographics of Thailand">66.7</a>
</td>
<td><a href="/wiki/Economy_of_Thailand" title="Economy of Thailand">425</a>
</td>
<td>.543
</td>
<td><a href="/wiki/National_Council_for_Peace_and_Order" title="National Council for Peace and Order">NCPO</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/2/26/Flag_of_East_Timor.svg/23px-Flag_of_East_Timor.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/2/26/Flag_of_East_Timor.svg/35px-Flag_of_East_Timor.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/2/26/Flag_of_East_Timor.svg/46px-Flag_of_East_Timor.svg.png 2x" data-file-width="900" data-file-height="450">&nbsp;</span>East Timor
</td>
<td>5 years
</td>
<td><a href="/wiki/2017_East_Timorese_parliamentary_election" title="2017 East Timorese parliamentary election"><span data-sort-value="000000002017-07-22-0000" style="white-space:nowrap">22 July 2017</span></a>
</td>
<td><span data-sort-value="000000002022-07-01-0000" style="white-space:nowrap">July 2022</span>
</td>
<td>5 years
</td>
<td><a href="/wiki/2017_East_Timorese_presidential_election" title="2017 East Timorese presidential election"><span data-sort-value="000000002017-03-20-0000" style="white-space:nowrap">20 March 2017</span></a>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>.386
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Flag_of_Turkey.svg/23px-Flag_of_Turkey.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Flag_of_Turkey.svg/35px-Flag_of_Turkey.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Flag_of_Turkey.svg/45px-Flag_of_Turkey.svg.png 2x" data-file-width="1200" data-file-height="800">&nbsp;</span>Turkey
</td>
<td>5 years
</td>
<td><a href="/wiki/2018_Turkish_general_election" title="2018 Turkish general election"><span data-sort-value="000000002018-06-24-0000" style="white-space:nowrap">24 June 2018</span></a>
</td>
<td><a href="/wiki/Next_Turkish_general_election" class="mw-redirect" title="Next Turkish general election"><span data-sort-value="000000002023-06-01-0000" style="white-space:nowrap">June 2023</span></a>
</td>
<td>5 years
</td>
<td><a href="/wiki/2018_Turkish_presidential_election" title="2018 Turkish presidential election"><span data-sort-value="000000002018-06-24-0000" style="white-space:nowrap">24 June 2018</span></a>
</td>
<td><a href="/wiki/Next_Turkish_general_election" class="mw-redirect" title="Next Turkish general election"><span data-sort-value="000000002023-01-01-0000" style="white-space:nowrap">2023</span></a>
</td>
<td>Political suppression,<sup id="cite_ref-16" class="reference"><a href="#cite_note-16">[16]</a></sup> voter fraud,<sup id="cite_ref-17" class="reference"><a href="#cite_note-17">[17]</a></sup><br>military interference<sup id="cite_ref-18" class="reference"><a href="#cite_note-18">[18]</a></sup>
</td>
<td><a href="/wiki/Demography_of_Turkey" class="mw-redirect" title="Demography of Turkey">75.6</a>
</td>
<td><a href="/wiki/Economy_of_Turkey" title="Economy of Turkey">774</a>
</td>
<td>.542
</td>
<td><a href="/wiki/Justice_and_Development_Party_(Turkey)" title="Justice and Development Party (Turkey)">AKP</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Flag_of_Turkmenistan.svg/23px-Flag_of_Turkmenistan.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Flag_of_Turkmenistan.svg/35px-Flag_of_Turkmenistan.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Flag_of_Turkmenistan.svg/45px-Flag_of_Turkmenistan.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Turkmenistan
</td>
<td>5 years
</td>
<td><a href="/wiki/2018_Turkmen_parliamentary_election" title="2018 Turkmen parliamentary election"><span data-sort-value="000000002018-03-25-0000" style="white-space:nowrap">25 March 2018</span></a>
</td>
<td><span data-sort-value="000000002023-03-01-0000" style="white-space:nowrap">March 2023</span>
</td>
<td>7 years
</td>
<td><a href="/wiki/2017_Turkmenistani_presidential_election" class="mw-redirect" title="2017 Turkmenistani presidential election"><span data-sort-value="000000002017-02-12-0000" style="white-space:nowrap">12 February 2017</span></a>
</td>
<td><span data-sort-value="000000002024-01-01-0000" style="white-space:nowrap">2024</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>no data
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/8/84/Flag_of_Uzbekistan.svg/23px-Flag_of_Uzbekistan.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/8/84/Flag_of_Uzbekistan.svg/35px-Flag_of_Uzbekistan.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/8/84/Flag_of_Uzbekistan.svg/46px-Flag_of_Uzbekistan.svg.png 2x" data-file-width="500" data-file-height="250">&nbsp;</span>Uzbekistan
</td>
<td>5 years
</td>
<td><a href="/wiki/Uzbekistani_parliamentary_election,_2014%E2%80%932015" class="mw-redirect" title="Uzbekistani parliamentary election, 2014–2015"><span data-sort-value="000000002014-12-21-0000" style="white-space:nowrap">21 December 2014</span></a>
</td>
<td><span data-sort-value="000000002019-12-01-0000" style="white-space:nowrap">December 2019</span>
</td>
<td>5 years
</td>
<td><a href="/wiki/2016_Uzbekistani_presidential_election" class="mw-redirect" title="2016 Uzbekistani presidential election"><span data-sort-value="000000002016-12-04-0000" style="white-space:nowrap">4 December 2016</span></a>
</td>
<td><span data-sort-value="000000002021-01-01-0000" style="white-space:nowrap">2021</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>.551
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/2/21/Flag_of_Vietnam.svg/23px-Flag_of_Vietnam.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/2/21/Flag_of_Vietnam.svg/35px-Flag_of_Vietnam.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/2/21/Flag_of_Vietnam.svg/45px-Flag_of_Vietnam.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Vietnam
</td>
<td>5 years
</td>
<td><a href="/wiki/2016_Vietnamese_legislative_election" title="2016 Vietnamese legislative election"><span data-sort-value="000000002016-05-22-0000" style="white-space:nowrap">22 May 2016</span></a>
</td>
<td><span data-sort-value="000000002021-05-01-0000" style="white-space:nowrap">May 2021</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>.531
</td>
<td><a href="/wiki/Communist_Party_of_Vietnam" title="Communist Party of Vietnam">Communist Party of Vietnam</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/8/89/Flag_of_Yemen.svg/23px-Flag_of_Yemen.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/8/89/Flag_of_Yemen.svg/35px-Flag_of_Yemen.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/8/89/Flag_of_Yemen.svg/45px-Flag_of_Yemen.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Yemen
</td>
<td>6 years
</td>
<td><a href="/wiki/2003_Yemeni_parliamentary_election" title="2003 Yemeni parliamentary election"><span data-sort-value="000000002003-04-27-0000" style="white-space:nowrap">27 April 2003</span></a>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/2012_Yemeni_presidential_election" title="2012 Yemeni presidential election"><span data-sort-value="000000002012-02-21-0000" style="white-space:nowrap">21 February 2012</span></a>
</td>
<td>
</td>
<td><a href="/wiki/Yemeni_Crisis" class="mw-redirect" title="Yemeni Crisis">Yemeni Crisis</a>, <a href="/wiki/Yemeni_Civil_War_(2015-present)" class="mw-redirect" title="Yemeni Civil War (2015-present)">Civil War</a>
</td>
<td>
</td>
<td>
</td>
<td>.310
</td>
<td>
</td></tr></tbody><tfoot></tfoot></table>
<table class="wikitable sortable jquery-tablesorter" style="font-size:90%;">

<thead><tr>
<th rowspan="2" class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">Country
</th>
<th colspan="3">Parliamentary election
</th>
<th colspan="3">Presidential election
</th>
<th rowspan="2" class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending"><a href="/wiki/Unfair_election" title="Unfair election">Fairness</a>
</th>
<th rowspan="2" class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending"><a href="/wiki/List_of_countries_by_population" class="mw-redirect" title="List of countries by population">Pop.</a><br>(m)
</th>
<th rowspan="2" class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending"><a href="/wiki/List_of_countries_by_GDP_(nominal)" title="List of countries by GDP (nominal)">GDP</a><br>($bn)
</th>
<th rowspan="2" class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending"><a href="/wiki/List_of_countries_by_inequality-adjusted_HDI" title="List of countries by inequality-adjusted HDI">IHDI</a>
</th>
<th rowspan="2" class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">In power now
</th>
<th rowspan="2" class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">Status of executive party(s) in legislature
</th></tr><tr>
<th class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">Term
</th>
<th class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">Last election
</th>
<th class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">Next election
</th>
<th class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">Term
</th>
<th class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">Last election
</th>
<th class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">Next election
</th></tr></thead><tbody>

<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/1/19/Flag_of_Andorra.svg/22px-Flag_of_Andorra.svg.png" decoding="async" width="22" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/1/19/Flag_of_Andorra.svg/33px-Flag_of_Andorra.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/1/19/Flag_of_Andorra.svg/43px-Flag_of_Andorra.svg.png 2x" data-file-width="1000" data-file-height="700">&nbsp;</span>Andorra
</td>
<td>4 Years
</td>
<td><a href="/wiki/2019_Andorran_parliamentary_election" title="2019 Andorran parliamentary election"><span data-sort-value="000000002019-04-07-0000" style="white-space:nowrap">7 April 2019</span></a>
</td>
<td><span data-sort-value="000000002023-04-01-0000" style="white-space:nowrap">April 2023</span>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Flag_of_Armenia.svg/23px-Flag_of_Armenia.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Flag_of_Armenia.svg/35px-Flag_of_Armenia.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Flag_of_Armenia.svg/46px-Flag_of_Armenia.svg.png 2x" data-file-width="1200" data-file-height="600">&nbsp;</span>Armenia
</td>
<td>5 years
</td>
<td><a href="/wiki/2017_Armenian_parliamentary_election" title="2017 Armenian parliamentary election"><span data-sort-value="000000002017-04-02-0000" style="white-space:nowrap">2 April 2017</span></a>
</td>
<td><span data-sort-value="000000002022-04-01-0000" style="white-space:nowrap">April 2022</span>
</td>
<td>5 years
</td>
<td><a href="/wiki/2018_Armenian_presidential_election" title="2018 Armenian presidential election"><span data-sort-value="000000002018-03-02-0000" style="white-space:nowrap">2 March 2018</span></a>
</td>
<td><span data-sort-value="000000002025-01-01-0000" style="white-space:nowrap">2025</span>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Armenia" title="Demographics of Armenia">3.3</a>
</td>
<td><a href="/wiki/Economy_of_Armenia" title="Economy of Armenia">10</a>
</td>
<td>.649
</td>
<td><a href="/wiki/Republican_Party_of_Armenia" title="Republican Party of Armenia">RPA</a>, <a href="/wiki/Armenian_Revolutionary_Federation" title="Armenian Revolutionary Federation">ARF</a>
</td>
<td>Majority Coalition
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/4/41/Flag_of_Austria.svg/23px-Flag_of_Austria.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/4/41/Flag_of_Austria.svg/35px-Flag_of_Austria.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/4/41/Flag_of_Austria.svg/45px-Flag_of_Austria.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Austria
</td>
<td>5 years
</td>
<td><a href="/wiki/2017_Austrian_legislative_election" title="2017 Austrian legislative election"><span data-sort-value="000000002017-10-15-0000" style="white-space:nowrap">15 October 2017</span></a>
</td>
<td><a href="/wiki/2019_Austrian_legislative_election" title="2019 Austrian legislative election"><span data-sort-value="000000002019-01-01-0000" style="white-space:nowrap">2019</span></a>
</td>
<td>6 years
</td>
<td><a href="/wiki/2016_Austrian_presidential_election" title="2016 Austrian presidential election"><span data-sort-value="000000002016-04-24-0000" style="white-space:nowrap">24 April 2016</span></a>
</td>
<td><span data-sort-value="000000002022-01-01-0000" style="white-space:nowrap">2022</span>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Austria" title="Demographics of Austria">8.5</a>
</td>
<td><a href="/wiki/Economy_of_Austria" title="Economy of Austria">418</a>
</td>
<td>.837
</td>
<td><a href="/wiki/Austrian_People%27s_Party" title="Austrian People's Party">ÖVP</a>, <a href="/wiki/Freedom_Party_of_Austria" title="Freedom Party of Austria">FPÖ</a>
</td>
<td>Majority Coalition
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Flag_of_Azerbaijan.svg/23px-Flag_of_Azerbaijan.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Flag_of_Azerbaijan.svg/35px-Flag_of_Azerbaijan.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Flag_of_Azerbaijan.svg/46px-Flag_of_Azerbaijan.svg.png 2x" data-file-width="1200" data-file-height="600">&nbsp;</span>Azerbaijan
</td>
<td>5 years
</td>
<td><a href="/wiki/2015_Azerbaijani_parliamentary_election" title="2015 Azerbaijani parliamentary election"><span data-sort-value="000000002015-11-21-0000" style="white-space:nowrap">21 November 2015</span></a>
</td>
<td><span data-sort-value="000000002020-11-01-0000" style="white-space:nowrap">November 2020</span>
</td>
<td>5 years
</td>
<td><a href="/wiki/2018_Azerbaijani_presidential_election" title="2018 Azerbaijani presidential election"><span data-sort-value="000000002018-04-11-0000" style="white-space:nowrap">11 April 2018</span></a>
</td>
<td><span data-sort-value="000000002025-01-01-0000" style="white-space:nowrap">2025</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/8/85/Flag_of_Belarus.svg/23px-Flag_of_Belarus.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/8/85/Flag_of_Belarus.svg/35px-Flag_of_Belarus.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/8/85/Flag_of_Belarus.svg/46px-Flag_of_Belarus.svg.png 2x" data-file-width="900" data-file-height="450">&nbsp;</span>Belarus
</td>
<td>4 years
</td>
<td><a href="/wiki/2016_Belarusian_parliamentary_election" title="2016 Belarusian parliamentary election"><span data-sort-value="000000002016-09-11-0000" style="white-space:nowrap">11 September 2016</span></a>
</td>
<td><span data-sort-value="000000002020-09-01-0000" style="white-space:nowrap">September 2020</span>
</td>
<td>4 years
</td>
<td><a href="/wiki/2015_Belarusian_presidential_election" title="2015 Belarusian presidential election"><span data-sort-value="000000002015-10-11-0000" style="white-space:nowrap">11 October 2015</span></a>
</td>
<td><a href="/w/index.php?title=2020_Belarusian_presidential_election&amp;action=edit&amp;redlink=1" class="new" title="2020 Belarusian presidential election (page does not exist)"><span data-sort-value="000000002020-01-01-0000" style="white-space:nowrap">2020</span></a>
</td>
<td>Disputed
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/9/92/Flag_of_Belgium_%28civil%29.svg/23px-Flag_of_Belgium_%28civil%29.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/9/92/Flag_of_Belgium_%28civil%29.svg/35px-Flag_of_Belgium_%28civil%29.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/9/92/Flag_of_Belgium_%28civil%29.svg/45px-Flag_of_Belgium_%28civil%29.svg.png 2x" data-file-width="450" data-file-height="300">&nbsp;</span>Belgium
</td>
<td>5 years
</td>
<td><a href="/wiki/2019_Belgian_federal_election" title="2019 Belgian federal election"><span data-sort-value="000000002019-05-26-0000" style="white-space:nowrap">26 May 2019</span></a>
</td>
<td><span data-sort-value="000000002024-01-01-0000" style="white-space:nowrap">2024</span>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>
</td>
<td><a href="/wiki/Demography_of_Belgium" class="mw-redirect" title="Demography of Belgium">11.2</a>
</td>
<td><a href="/wiki/Economy_of_Belgium" title="Economy of Belgium">514</a>
</td>
<td>.825
</td>
<td><a href="/wiki/Mouvement_R%C3%A9formateur" title="Mouvement Réformateur">MR</a>, <a href="/wiki/Christen-Democratisch_en_Vlaams" title="Christen-Democratisch en Vlaams">CD&amp;V</a>, <a href="/wiki/Open_Vlaamse_Liberalen_en_Democraten" title="Open Vlaamse Liberalen en Democraten">Open VLD</a>
</td>
<td>Minority Coalition
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Flag_of_Bosnia_and_Herzegovina.svg/23px-Flag_of_Bosnia_and_Herzegovina.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Flag_of_Bosnia_and_Herzegovina.svg/35px-Flag_of_Bosnia_and_Herzegovina.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Flag_of_Bosnia_and_Herzegovina.svg/46px-Flag_of_Bosnia_and_Herzegovina.svg.png 2x" data-file-width="800" data-file-height="400">&nbsp;</span>Bosnia and Herzegovina
</td>
<td>4 years
</td>
<td><a href="/wiki/2018_Bosnian_general_election" title="2018 Bosnian general election"><span data-sort-value="000000002018-10-07-0000" style="white-space:nowrap">7 October 2018</span></a>
</td>
<td><span data-sort-value="000000002022-10-01-0000" style="white-space:nowrap">October 2022</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Bosnia_and_Herzegovina" title="Demographics of Bosnia and Herzegovina">3.8</a>
</td>
<td><a href="/wiki/Economy_of_Bosnia_and_Herzegovina" title="Economy of Bosnia and Herzegovina">17</a>
</td>
<td>.650
</td>
<td><a href="/wiki/Social_Democratic_Party_of_Bosnia_and_Herzegovina" title="Social Democratic Party of Bosnia and Herzegovina">Multiple</a>
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Flag_of_Bulgaria.svg/23px-Flag_of_Bulgaria.svg.png" decoding="async" width="23" height="14" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Flag_of_Bulgaria.svg/35px-Flag_of_Bulgaria.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Flag_of_Bulgaria.svg/46px-Flag_of_Bulgaria.svg.png 2x" data-file-width="1000" data-file-height="600">&nbsp;</span>Bulgaria
</td>
<td>4 years
</td>
<td><a href="/wiki/2017_Bulgarian_parliamentary_election" title="2017 Bulgarian parliamentary election"><span data-sort-value="000000002017-03-26-0000" style="white-space:nowrap">26 March 2017</span></a>
</td>
<td><span data-sort-value="000000002021-03-01-0000" style="white-space:nowrap">March 2021</span>
</td>
<td>4 years
</td>
<td><a href="/wiki/2016_Bulgarian_presidential_election" title="2016 Bulgarian presidential election"><span data-sort-value="000000002016-11-06-0000" style="white-space:nowrap">6 November 2016</span></a>
</td>
<td><a href="/wiki/2021_Bulgarian_presidential_election" title="2021 Bulgarian presidential election"><span data-sort-value="000000002021-01-01-0000" style="white-space:nowrap">2021</span></a>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Bulgaria" title="Demographics of Bulgaria">6.9</a>
</td>
<td><a href="/wiki/Economy_of_Bulgaria" title="Economy of Bulgaria">51</a>
</td>
<td>.704
</td>
<td><a href="/wiki/GERB" title="GERB">GERB</a>, <a href="/wiki/Reformist_Bloc" title="Reformist Bloc">Reformist Bloc</a>
</td>
<td>Minority Coalition; confidence from <a href="/wiki/Patriotic_Front_(Bulgaria)" title="Patriotic Front (Bulgaria)">Patriotic Front</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Flag_of_Croatia.svg/23px-Flag_of_Croatia.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Flag_of_Croatia.svg/35px-Flag_of_Croatia.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Flag_of_Croatia.svg/46px-Flag_of_Croatia.svg.png 2x" data-file-width="1200" data-file-height="600">&nbsp;</span>Croatia
</td>
<td>4 years
</td>
<td><a href="/wiki/2016_Croatian_parliamentary_election" title="2016 Croatian parliamentary election"><span data-sort-value="000000002016-09-11-0000" style="white-space:nowrap">11 September 2016</span></a>
</td>
<td><a href="/wiki/Next_Croatian_parliamentary_election" title="Next Croatian parliamentary election"><span data-sort-value="000000002020-12-01-0000" style="white-space:nowrap">December 2020</span></a>
</td>
<td>5 years
</td>
<td><a href="/wiki/2014%E2%80%9315_Croatian_presidential_election" title="2014–15 Croatian presidential election"><span data-sort-value="000000002014-12-28-0000" style="white-space:nowrap">28 December 2014</span></a>
</td>
<td><a href="/wiki/Next_Croatian_presidential_election" title="Next Croatian presidential election"><span data-sort-value="000000002020-01-01-0000" style="white-space:nowrap">2020</span></a>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Croatia" title="Demographics of Croatia">4.2</a>
</td>
<td><a href="/wiki/Economy_of_Croatia" title="Economy of Croatia">64</a>
</td>
<td>.683
</td>
<td><a href="/wiki/Croatian_Democratic_Union" title="Croatian Democratic Union">HDZ</a>, <a href="/wiki/Croatian_People%27s_Party_%E2%80%93_Liberal_Democrats" title="Croatian People's Party – Liberal Democrats">HNS − LD</a>
</td>
<td>Minority Coalition; confidence from 16 other MPs
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Flag_of_Cyprus.svg/23px-Flag_of_Cyprus.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Flag_of_Cyprus.svg/35px-Flag_of_Cyprus.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Flag_of_Cyprus.svg/45px-Flag_of_Cyprus.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Cyprus
</td>
<td>5 years
</td>
<td><a href="/wiki/2016_Cypriot_legislative_election" title="2016 Cypriot legislative election"><span data-sort-value="000000002016-05-22-0000" style="white-space:nowrap">22 May 2016</span></a>
</td>
<td><span data-sort-value="000000002020-05-01-0000" style="white-space:nowrap">May 2020</span>
</td>
<td>5 years
</td>
<td><a href="/wiki/2018_Cypriot_presidential_election" title="2018 Cypriot presidential election"><span data-sort-value="000000002018-01-28-0000" style="white-space:nowrap">28 January 2018</span></a>
</td>
<td><span data-sort-value="000000002023-01-01-0000" style="white-space:nowrap">2023</span>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Cyprus" title="Demographics of Cyprus">1.1</a>
</td>
<td><a href="/wiki/Economy_of_Cyprus" title="Economy of Cyprus">23</a>
</td>
<td>.751
</td>
<td><a href="/wiki/Democratic_Rally" title="Democratic Rally">Democratic Rally</a>
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/c/cb/Flag_of_the_Czech_Republic.svg/23px-Flag_of_the_Czech_Republic.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/c/cb/Flag_of_the_Czech_Republic.svg/35px-Flag_of_the_Czech_Republic.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/c/cb/Flag_of_the_Czech_Republic.svg/45px-Flag_of_the_Czech_Republic.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Czech Republic
</td>
<td>4 years
</td>
<td><a href="/wiki/2017_Czech_legislative_election" title="2017 Czech legislative election"><span data-sort-value="000000002017-10-20-0000" style="white-space:nowrap">20 October 2017</span></a>
</td>
<td><a href="/wiki/Next_Czech_legislative_election" title="Next Czech legislative election"><span data-sort-value="000000002021-10-01-0000" style="white-space:nowrap">October 2021</span></a>
</td>
<td>5 years
</td>
<td><a href="/wiki/2018_Czech_presidential_election" title="2018 Czech presidential election"><span data-sort-value="000000002018-01-12-0000" style="white-space:nowrap">12 January 2018</span></a>
</td>
<td><a href="/wiki/2023_Czech_presidential_election" class="mw-redirect" title="2023 Czech presidential election"><span data-sort-value="000000002023-01-01-0000" style="white-space:nowrap">2023</span></a>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_the_Czech_Republic" title="Demographics of the Czech Republic">10.5</a>
</td>
<td><a href="/wiki/Economy_of_the_Czech_Republic" title="Economy of the Czech Republic">214</a>
</td>
<td>.826
</td>
<td><a href="/wiki/ANO_2011" title="ANO 2011">ANO 2011</a>
</td>
<td><a href="/wiki/ANO_2011" title="ANO 2011">ANO 2011</a> – <a href="/wiki/Czech_Social_Democratic_Party" title="Czech Social Democratic Party">Czech Social Democratic Party</a> Minority + support of <a href="/wiki/Communist_Party_of_Bohemia_and_Moravia" title="Communist Party of Bohemia and Moravia">Communist Party of Bohemia and Moravia</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Flag_of_Denmark.svg/20px-Flag_of_Denmark.svg.png" decoding="async" width="20" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Flag_of_Denmark.svg/31px-Flag_of_Denmark.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Flag_of_Denmark.svg/40px-Flag_of_Denmark.svg.png 2x" data-file-width="740" data-file-height="560">&nbsp;</span>Denmark
</td>
<td>4 years
</td>
<td><a href="/wiki/2019_Danish_general_election" title="2019 Danish general election"><span data-sort-value="000000002019-06-17-0000" style="white-space:nowrap">17 June 2019</span></a>
</td>
<td><a href="/wiki/Next_Danish_general_election" class="mw-redirect" title="Next Danish general election"><span data-sort-value="000000002023-01-01-0000" style="white-space:nowrap">2023</span></a>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Denmark" title="Demographics of Denmark">5.6</a>
</td>
<td><a href="/wiki/Economy_of_Denmark" title="Economy of Denmark">332</a>
</td>
<td>.845
</td>
<td>TBD
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Flag_of_Estonia.svg/23px-Flag_of_Estonia.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Flag_of_Estonia.svg/35px-Flag_of_Estonia.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Flag_of_Estonia.svg/46px-Flag_of_Estonia.svg.png 2x" data-file-width="990" data-file-height="630">&nbsp;</span>Estonia
</td>
<td>4 years
</td>
<td><a href="/wiki/2019_Estonian_parliamentary_election" title="2019 Estonian parliamentary election"><span data-sort-value="000000002019-03-03-0000" style="white-space:nowrap">3 March 2019</span></a>
</td>
<td><span data-sort-value="000000002023-03-05-0000" style="white-space:nowrap">5 March 2023</span>
</td>
<td>
</td>
<td><a href="/wiki/2016_Estonian_presidential_election" title="2016 Estonian presidential election"><span data-sort-value="000000002016-10-03-0000" style="white-space:nowrap">3 October 2016</span></a>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Estonia" title="Demographics of Estonia">1.3</a>
</td>
<td><a href="/wiki/Economy_of_Estonia" title="Economy of Estonia">21</a>
</td>
<td>.770
</td>
<td><a href="/wiki/Estonian_Centre_Party" title="Estonian Centre Party">Estonian Centre Party</a>, <a href="/wiki/Social_Democratic_Party_(Estonia)" title="Social Democratic Party (Estonia)">SDE</a>, <a href="/wiki/Pro_Patria_and_Res_Publica_Union" class="mw-redirect" title="Pro Patria and Res Publica Union">IRL</a>
</td>
<td>Majority Coalition
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Flag_of_Finland.svg/23px-Flag_of_Finland.svg.png" decoding="async" width="23" height="14" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Flag_of_Finland.svg/35px-Flag_of_Finland.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Flag_of_Finland.svg/46px-Flag_of_Finland.svg.png 2x" data-file-width="1800" data-file-height="1100">&nbsp;</span>Finland
</td>
<td>4 years
</td>
<td><a href="/wiki/2019_Finnish_parliamentary_election" title="2019 Finnish parliamentary election"><span data-sort-value="000000002019-04-14-0000" style="white-space:nowrap">14 April 2019</span></a>
</td>
<td><span data-sort-value="000000002023-04-01-0000" style="white-space:nowrap">April 2023</span>
</td>
<td>6 years
</td>
<td><a href="/wiki/2018_Finnish_presidential_election" title="2018 Finnish presidential election"><span data-sort-value="000000002018-01-28-0000" style="white-space:nowrap">28 January 2018</span></a>
</td>
<td><span data-sort-value="000000002024-01-01-0000" style="white-space:nowrap">January 2024</span>
</td>
<td>
</td>
<td><a href="/wiki/Demography_of_Finland" class="mw-redirect" title="Demography of Finland">5.4</a>
</td>
<td><a href="/wiki/Economy_of_Finland" title="Economy of Finland">263</a>
</td>
<td>.839
</td>
<td><a href="/wiki/Centre_Party_(Finland)" title="Centre Party (Finland)">Centre Party</a>, <a href="/wiki/Finns_Party" title="Finns Party">Finns Party</a>, <a href="/wiki/National_Coalition_Party" title="National Coalition Party">National Coalition Party</a>
</td>
<td>Majority Coalition
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/en/thumb/c/c3/Flag_of_France.svg/23px-Flag_of_France.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/en/thumb/c/c3/Flag_of_France.svg/35px-Flag_of_France.svg.png 1.5x, //upload.wikimedia.org/wikipedia/en/thumb/c/c3/Flag_of_France.svg/45px-Flag_of_France.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>France
</td>
<td>5 years
</td>
<td><a href="/wiki/2017_French_legislative_election" title="2017 French legislative election"><span data-sort-value="000000002017-06-11-0000" style="white-space:nowrap">11 June 2017</span></a>
</td>
<td><span data-sort-value="000000002022-06-01-0000" style="white-space:nowrap">June 2022</span>
</td>
<td>5 years
</td>
<td><a href="/wiki/2017_French_presidential_election" title="2017 French presidential election"><span data-sort-value="000000002017-04-23-0000" style="white-space:nowrap">23 April 2017</span></a>
</td>
<td><a href="/wiki/2022_French_presidential_election" title="2022 French presidential election"><span data-sort-value="000000002022-04-01-0000" style="white-space:nowrap">April 2022</span></a>
</td>
<td>
</td>
<td><a href="/wiki/Demography_of_France" class="mw-redirect" title="Demography of France">65.7</a>
</td>
<td><a href="/wiki/Economy_of_France" title="Economy of France">2,775</a>
</td>
<td>.812
</td>
<td><i><a href="/wiki/Emmanuel_Macron" title="Emmanuel Macron">Emmanuel Macron</a></i>
<p><a href="/wiki/En_Marche!" class="mw-redirect" title="En Marche!">En Marche!</a>
</p>
</td>
<td>Majority
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Flag_of_Georgia.svg/23px-Flag_of_Georgia.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Flag_of_Georgia.svg/35px-Flag_of_Georgia.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Flag_of_Georgia.svg/45px-Flag_of_Georgia.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Georgia
</td>
<td>4 years
</td>
<td><a href="/wiki/2016_Georgian_parliamentary_election" title="2016 Georgian parliamentary election"><span data-sort-value="000000002016-10-08-0000" style="white-space:nowrap">8 October 2016</span></a>
</td>
<td><a href="/wiki/Next_Georgian_parliamentary_election" title="Next Georgian parliamentary election"><span data-sort-value="000000002020-10-01-0000" style="white-space:nowrap">October 2020</span></a>
</td>
<td>
</td>
<td><a href="/wiki/2016_Georgian_parliamentary_election" title="2016 Georgian parliamentary election"><span data-sort-value="000000002016-10-08-0000" style="white-space:nowrap">8 October 2016</span></a>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/en/thumb/b/ba/Flag_of_Germany.svg/23px-Flag_of_Germany.svg.png" decoding="async" width="23" height="14" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/en/thumb/b/ba/Flag_of_Germany.svg/35px-Flag_of_Germany.svg.png 1.5x, //upload.wikimedia.org/wikipedia/en/thumb/b/ba/Flag_of_Germany.svg/46px-Flag_of_Germany.svg.png 2x" data-file-width="1000" data-file-height="600">&nbsp;</span>Germany
</td>
<td>4 years<sup id="cite_ref-19" class="reference"><a href="#cite_note-19">[19]</a></sup>
</td>
<td><a href="/wiki/2017_German_federal_election" title="2017 German federal election"><span data-sort-value="000000002017-09-24-0000" style="white-space:nowrap">24 September 2017</span></a>
</td>
<td><a href="/wiki/Next_German_federal_election" title="Next German federal election"><span data-sort-value="000000002021-08-01-0000" style="white-space:nowrap">August 2021</span></a>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/Demography_of_Germany" class="mw-redirect" title="Demography of Germany">80.4</a>
</td>
<td><a href="/wiki/Economy_of_Germany" title="Economy of Germany">3,604</a>
</td>
<td>.856
</td>
<td><a href="/wiki/Christian_Democratic_Union_of_Germany" title="Christian Democratic Union of Germany">CDU</a>/<a href="/wiki/Christian_Social_Union_in_Bavaria" title="Christian Social Union in Bavaria">CSU</a>, <a href="/wiki/Social_Democratic_Party_of_Germany" title="Social Democratic Party of Germany">SPD</a>
</td>
<td>Majority Coalition
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/0/02/Flag_of_Gibraltar.svg/23px-Flag_of_Gibraltar.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/0/02/Flag_of_Gibraltar.svg/35px-Flag_of_Gibraltar.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/0/02/Flag_of_Gibraltar.svg/46px-Flag_of_Gibraltar.svg.png 2x" data-file-width="1000" data-file-height="500">&nbsp;</span>Gibraltar
</td>
<td>4 years
</td>
<td><a href="/wiki/2015_Gibraltar_general_election" title="2015 Gibraltar general election"><span data-sort-value="000000002015-11-26-0000" style="white-space:nowrap">26 November 2015</span></a>
</td>
<td><a href="/w/index.php?title=2019_Gibraltar_general_election&amp;action=edit&amp;redlink=1" class="new" title="2019 Gibraltar general election (page does not exist)"><span data-sort-value="000000002019-11-01-0000" style="white-space:nowrap">November 2019</span></a>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Gibraltar" title="Demographics of Gibraltar">.030</a>
</td>
<td><a href="/wiki/Economy_of_Gibraltar" title="Economy of Gibraltar">1.106</a>
</td>
<td>.961
</td>
<td><a href="/wiki/Gibraltar_Socialist_Labour_Party" title="Gibraltar Socialist Labour Party">GSLP</a>/<a href="/wiki/Gibraltar_Liberal_Party" class="mw-redirect" title="Gibraltar Liberal Party">Liberal</a> Alliance
</td>
<td>Majority
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Flag_of_Greece.svg/23px-Flag_of_Greece.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Flag_of_Greece.svg/35px-Flag_of_Greece.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Flag_of_Greece.svg/45px-Flag_of_Greece.svg.png 2x" data-file-width="600" data-file-height="400">&nbsp;</span>Greece
</td>
<td>4 years
</td>
<td><a href="/wiki/September_2015_Greek_legislative_election" title="September 2015 Greek legislative election"><span data-sort-value="000000002015-09-20-0000" style="white-space:nowrap">20 September 2015</span></a>
</td>
<td><a href="/wiki/Next_Greek_legislative_election" class="mw-redirect" title="Next Greek legislative election"><span data-sort-value="000000002019-10-20-0000" style="white-space:nowrap">20 October 2019</span></a>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Greece" title="Demographics of Greece">10.8</a>
</td>
<td><a href="/wiki/Economy_of_Greece" title="Economy of Greece">299</a>
</td>
<td>.760
</td>
<td><a href="/wiki/SYRIZA" class="mw-redirect" title="SYRIZA">SYRIZA</a>, <a href="/wiki/Independent_Greeks" title="Independent Greeks">ANEL</a>
</td>
<td>Majority Coalition
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Flag_of_Hungary.svg/23px-Flag_of_Hungary.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Flag_of_Hungary.svg/35px-Flag_of_Hungary.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Flag_of_Hungary.svg/46px-Flag_of_Hungary.svg.png 2x" data-file-width="1200" data-file-height="600">&nbsp;</span>Hungary
</td>
<td>4 years
</td>
<td><a href="/wiki/2018_Hungarian_parliamentary_election" title="2018 Hungarian parliamentary election"><span data-sort-value="000000002018-04-08-0000" style="white-space:nowrap">8 April 2018</span></a>
</td>
<td><a href="/wiki/Next_Hungarian_parliamentary_election" class="mw-redirect" title="Next Hungarian parliamentary election"><span data-sort-value="000000002022-04-01-0000" style="white-space:nowrap">April 2022</span></a>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Hungary" title="Demographics of Hungary">9.9</a>
</td>
<td><a href="/wiki/Economy_of_Hungary" title="Economy of Hungary">138</a>
</td>
<td>.769
</td>
<td><a href="/wiki/Fidesz" title="Fidesz">Fidesz</a>, <a href="/wiki/Christian_Democratic_People%27s_Party_(Hungary)" title="Christian Democratic People's Party (Hungary)">KDNP</a>
</td>
<td>Majority Coalition
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Flag_of_Iceland.svg/21px-Flag_of_Iceland.svg.png" decoding="async" width="21" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Flag_of_Iceland.svg/32px-Flag_of_Iceland.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Flag_of_Iceland.svg/42px-Flag_of_Iceland.svg.png 2x" data-file-width="800" data-file-height="576">&nbsp;</span>Iceland
</td>
<td>4 years
</td>
<td><a href="/wiki/2017_Icelandic_parliamentary_election" title="2017 Icelandic parliamentary election"><span data-sort-value="000000002017-10-28-0000" style="white-space:nowrap">28 October 2017</span></a>
</td>
<td><a href="/wiki/Next_Icelandic_parliamentary_election" title="Next Icelandic parliamentary election"><span data-sort-value="000000002021-10-23-0000" style="white-space:nowrap">23 October 2021</span></a>
</td>
<td>4 years
</td>
<td><a href="/wiki/2016_Icelandic_presidential_election" title="2016 Icelandic presidential election"><span data-sort-value="000000002016-06-25-0000" style="white-space:nowrap">25 June 2016</span></a>
</td>
<td><span data-sort-value="000000002020-01-01-0000" style="white-space:nowrap">2020</span>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Iceland" title="Demographics of Iceland">0.3</a>
</td>
<td><a href="/wiki/Economy_of_Iceland" title="Economy of Iceland">13</a>
</td>
<td>.848
</td>
<td><a href="/wiki/Progressive_Party_(Iceland)" title="Progressive Party (Iceland)">Progressive Party</a>, <a href="/wiki/Independence_Party_(Iceland)" title="Independence Party (Iceland)">Independence Party</a>
</td>
<td>Majority Coalition
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/4/45/Flag_of_Ireland.svg/23px-Flag_of_Ireland.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/4/45/Flag_of_Ireland.svg/35px-Flag_of_Ireland.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/4/45/Flag_of_Ireland.svg/46px-Flag_of_Ireland.svg.png 2x" data-file-width="1200" data-file-height="600">&nbsp;</span>Ireland
</td>
<td>5 years<sup id="cite_ref-20" class="reference"><a href="#cite_note-20">[20]</a></sup>
</td>
<td><a href="/wiki/2016_Irish_general_election" title="2016 Irish general election"><span data-sort-value="000000002016-02-26-0000" style="white-space:nowrap">26 February 2016</span></a>
</td>
<td><a href="/wiki/Next_Irish_general_election" title="Next Irish general election"><span data-sort-value="000000002021-04-10-0000" style="white-space:nowrap">10 April 2021</span></a>
</td>
<td>7 years<sup id="cite_ref-21" class="reference"><a href="#cite_note-21">[21]</a></sup>
</td>
<td><a href="/wiki/2018_Irish_presidential_election" title="2018 Irish presidential election"><span data-sort-value="000000002018-10-26-0000" style="white-space:nowrap">26 October 2018</span></a>
</td>
<td><a href="/w/index.php?title=2025_Irish_presidential_election&amp;action=edit&amp;redlink=1" class="new" title="2025 Irish presidential election (page does not exist)"><span data-sort-value="000000002025-10-01-0000" style="white-space:nowrap">October 2025</span></a>
</td>
<td>
</td>
<td><a href="/wiki/Demography_of_Ireland" class="mw-redirect" title="Demography of Ireland">4.6</a>
</td>
<td><a href="/wiki/Economy_of_the_Republic_of_Ireland" title="Economy of the Republic of Ireland">221</a>
</td>
<td>.850
</td>
<td><a href="/wiki/Fine_Gael" title="Fine Gael">Fine Gael</a>, <a href="/wiki/Independent_politician" title="Independent politician">Independents</a>
</td>
<td>Minority Coalition; confidence from <a href="/wiki/Fianna_F%C3%A1il" title="Fianna Fáil">Fianna Fáil</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/en/thumb/0/03/Flag_of_Italy.svg/23px-Flag_of_Italy.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/en/thumb/0/03/Flag_of_Italy.svg/35px-Flag_of_Italy.svg.png 1.5x, //upload.wikimedia.org/wikipedia/en/thumb/0/03/Flag_of_Italy.svg/45px-Flag_of_Italy.svg.png 2x" data-file-width="1500" data-file-height="1000">&nbsp;</span>Italy
</td>
<td>5 years
</td>
<td><a href="/wiki/2018_Italian_general_election" title="2018 Italian general election"><span data-sort-value="000000002018-03-04-0000" style="white-space:nowrap">4 March 2018</span></a>
</td>
<td><a href="/wiki/Next_Italian_general_election" title="Next Italian general election"><span data-sort-value="000000002023-05-28-0000" style="white-space:nowrap">28 May 2023</span></a>
</td>
<td>
</td>
<td><span data-sort-value="000000002015-01-29-0000" style="white-space:nowrap">29 January 2015</span>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/Demography_of_Italy" class="mw-redirect" title="Demography of Italy">60.4</a>
</td>
<td><a href="/wiki/Economy_of_Italy" title="Economy of Italy">2,195</a>
</td>
<td>.776
</td>
<td><a href="/wiki/Five_Star_Movement" title="Five Star Movement">Five Star Movement</a>, <a href="/wiki/Lega_Nord" title="Lega Nord">Lega Nord</a>
</td>
<td>Majority Coalition
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Flag_of_Kosovo.svg/21px-Flag_of_Kosovo.svg.png" decoding="async" width="21" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Flag_of_Kosovo.svg/32px-Flag_of_Kosovo.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Flag_of_Kosovo.svg/42px-Flag_of_Kosovo.svg.png 2x" data-file-width="840" data-file-height="600">&nbsp;</span>Kosovo
</td>
<td>4 years
</td>
<td><a href="/wiki/2017_Kosovan_parliamentary_election" title="2017 Kosovan parliamentary election"><span data-sort-value="000000002017-06-11-0000" style="white-space:nowrap">11 June 2017</span></a>
</td>
<td><span data-sort-value="000000002020-01-01-0000" style="white-space:nowrap">2020</span>
</td>
<td>
</td>
<td><a href="/wiki/2016_Kosovan_presidential_election" title="2016 Kosovan presidential election"><span data-sort-value="000000002016-02-26-0000" style="white-space:nowrap">26 February 2016</span></a>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/8/84/Flag_of_Latvia.svg/23px-Flag_of_Latvia.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/8/84/Flag_of_Latvia.svg/35px-Flag_of_Latvia.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/8/84/Flag_of_Latvia.svg/46px-Flag_of_Latvia.svg.png 2x" data-file-width="1200" data-file-height="600">&nbsp;</span>Latvia
</td>
<td>4 years
</td>
<td><a href="/wiki/2018_Latvian_parliamentary_election" title="2018 Latvian parliamentary election"><span data-sort-value="000000002018-10-26-0000" style="white-space:nowrap">26 October 2018</span></a>
</td>
<td><a href="/wiki/2022_Latvian_parliamentary_election" title="2022 Latvian parliamentary election"><span data-sort-value="000000002022-10-01-0000" style="white-space:nowrap">1 October 2022</span></a>
</td>
<td>
</td>
<td><a href="/wiki/2015_Latvian_presidential_election" title="2015 Latvian presidential election"><span data-sort-value="000000002015-06-03-0000" style="white-space:nowrap">3 June 2015</span></a>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Latvia" title="Demographics of Latvia">2.0</a>
</td>
<td><a href="/wiki/Economy_of_Latvia" title="Economy of Latvia">28</a>
</td>
<td>.726
</td>
<td><a href="/wiki/Unity_(Latvian_political_party)" class="mw-redirect" title="Unity (Latvian political party)">Unity</a>, <a href="/wiki/Union_of_Greens_and_Farmers" title="Union of Greens and Farmers">ZZS</a>, <a href="/wiki/National_Alliance_(Latvia)" title="National Alliance (Latvia)">NA</a>
</td>
<td>Majority Coalition
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/1/11/Flag_of_Lithuania.svg/23px-Flag_of_Lithuania.svg.png" decoding="async" width="23" height="14" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/1/11/Flag_of_Lithuania.svg/35px-Flag_of_Lithuania.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/1/11/Flag_of_Lithuania.svg/46px-Flag_of_Lithuania.svg.png 2x" data-file-width="500" data-file-height="300">&nbsp;</span>Lithuania
</td>
<td>4 years
</td>
<td><a href="/wiki/2016_Lithuanian_parliamentary_election" title="2016 Lithuanian parliamentary election"><span data-sort-value="000000002016-10-09-0000" style="white-space:nowrap">9 October 2016</span></a>
</td>
<td><span data-sort-value="000000002020-10-01-0000" style="white-space:nowrap">October 2020</span>
</td>
<td>5 years
</td>
<td><a href="/wiki/2014_Lithuanian_presidential_election" title="2014 Lithuanian presidential election"><span data-sort-value="000000002014-05-11-0000" style="white-space:nowrap">11 May 2014</span></a>
</td>
<td><a href="/wiki/2019_Lithuanian_presidential_election" title="2019 Lithuanian presidential election"><span data-sort-value="000000002019-05-12-0000" style="white-space:nowrap">12 May 2019</span></a>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Lithuania" title="Demographics of Lithuania">2.9</a>
</td>
<td><a href="/wiki/Economy_of_Lithuania" title="Economy of Lithuania">42</a>
</td>
<td>.727
</td>
<td><a href="/wiki/Lithuanian_Farmers_and_Greens_Union" title="Lithuanian Farmers and Greens Union">Peasants</a>
</td>
<td>Minority Government
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/d/da/Flag_of_Luxembourg.svg/23px-Flag_of_Luxembourg.svg.png" decoding="async" width="23" height="14" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/d/da/Flag_of_Luxembourg.svg/35px-Flag_of_Luxembourg.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/d/da/Flag_of_Luxembourg.svg/46px-Flag_of_Luxembourg.svg.png 2x" data-file-width="1000" data-file-height="600">&nbsp;</span>Luxembourg
</td>
<td>5 years
</td>
<td><a href="/wiki/2018_Luxembourg_general_election" title="2018 Luxembourg general election"><span data-sort-value="000000002018-10-14-0000" style="white-space:nowrap">14 October 2018</span></a>
</td>
<td><span data-sort-value="000000002023-10-01-0000" style="white-space:nowrap">October 2023</span>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Luxembourg" title="Demographics of Luxembourg">.537</a>
</td>
<td><a href="/wiki/Economy_of_Luxembourg" title="Economy of Luxembourg">42</a>
</td>
<td>.813
</td>
<td><a href="/wiki/Democratic_Party_(Luxembourg)" title="Democratic Party (Luxembourg)">DP</a>, <a href="/wiki/Luxembourg_Socialist_Workers%27_Party" title="Luxembourg Socialist Workers' Party">LSAP</a>, <a href="/wiki/The_Greens_(Luxembourg)" title="The Greens (Luxembourg)">DG</a>
</td>
<td>Majority Coalition
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/7/79/Flag_of_North_Macedonia.svg/23px-Flag_of_North_Macedonia.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/7/79/Flag_of_North_Macedonia.svg/35px-Flag_of_North_Macedonia.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/7/79/Flag_of_North_Macedonia.svg/46px-Flag_of_North_Macedonia.svg.png 2x" data-file-width="1680" data-file-height="840">&nbsp;</span>Macedonia
</td>
<td>4 years
</td>
<td><a href="/wiki/2016_Macedonian_parliamentary_election" title="2016 Macedonian parliamentary election"><span data-sort-value="000000002016-12-11-0000" style="white-space:nowrap">11 December 2016</span></a>
</td>
<td><span data-sort-value="000000002020-12-01-0000" style="white-space:nowrap">December 2020</span>
</td>
<td>5 years
</td>
<td><a href="/wiki/2019_North_Macedonian_presidential_election" title="2019 North Macedonian presidential election"><span data-sort-value="000000002019-04-21-0000" style="white-space:nowrap">21 April 2019</span></a>
</td>
<td><span data-sort-value="000000002024-01-01-0000" style="white-space:nowrap">2024</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/VMRO-DPMNE" title="VMRO-DPMNE">VMRO-DPMNE</a> and <a href="/wiki/Democratic_Union_for_Integration" title="Democratic Union for Integration">Democratic Union for Integration</a> coalition
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/7/73/Flag_of_Malta.svg/23px-Flag_of_Malta.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/7/73/Flag_of_Malta.svg/35px-Flag_of_Malta.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/7/73/Flag_of_Malta.svg/45px-Flag_of_Malta.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Malta
</td>
<td>5 years
</td>
<td><a href="/wiki/2017_Maltese_general_election" title="2017 Maltese general election"><span data-sort-value="000000002017-06-03-0000" style="white-space:nowrap">3 June 2017</span></a>
</td>
<td><a href="/wiki/Next_Maltese_general_election" title="Next Maltese general election"><span data-sort-value="000000002022-06-01-0000" style="white-space:nowrap">June 2022</span></a>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Malta" title="Demographics of Malta">.452</a>
</td>
<td><a href="/wiki/Economy_of_Malta" title="Economy of Malta">9</a>
</td>
<td>.778
</td>
<td><a href="/wiki/Labour_Party_(Malta)" title="Labour Party (Malta)">Labour</a>
</td>
<td>Majority
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Flag_of_Monaco.svg/19px-Flag_of_Monaco.svg.png" decoding="async" width="19" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Flag_of_Monaco.svg/29px-Flag_of_Monaco.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Flag_of_Monaco.svg/38px-Flag_of_Monaco.svg.png 2x" data-file-width="750" data-file-height="600">&nbsp;</span>Monaco
</td>
<td>5 years
</td>
<td><a href="/wiki/2018_Monegasque_general_election" title="2018 Monegasque general election"><span data-sort-value="000000002018-02-11-0000" style="white-space:nowrap">11 February 2018</span></a>
</td>
<td><a href="/w/index.php?title=2023_Monegasque_general_election&amp;action=edit&amp;redlink=1" class="new" title="2023 Monegasque general election (page does not exist)"><span data-sort-value="000000002023-02-01-0000" style="white-space:nowrap">February 2023</span></a>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/2/27/Flag_of_Moldova.svg/23px-Flag_of_Moldova.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/2/27/Flag_of_Moldova.svg/35px-Flag_of_Moldova.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/2/27/Flag_of_Moldova.svg/46px-Flag_of_Moldova.svg.png 2x" data-file-width="1800" data-file-height="900">&nbsp;</span>Moldova
</td>
<td>4 years
</td>
<td><a href="/wiki/2019_Moldovan_parliamentary_election" title="2019 Moldovan parliamentary election"><span data-sort-value="000000002019-02-24-0000" style="white-space:nowrap">24 February 2019</span></a>
</td>
<td><span data-sort-value="000000002024-01-01-0000" style="white-space:nowrap">2024</span>
</td>
<td>4 years
</td>
<td><a href="/wiki/2016_Moldovan_presidential_election" title="2016 Moldovan presidential election"><span data-sort-value="000000002016-10-30-0000" style="white-space:nowrap">30 October 2016</span></a>
</td>
<td><span data-sort-value="000000002020-01-01-0000" style="white-space:nowrap">2020</span>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Moldova" title="Demographics of Moldova">3.6</a>
</td>
<td><a href="/wiki/Economy_of_Moldova" title="Economy of Moldova">7</a>
</td>
<td>.660
</td>
<td><a href="/wiki/Liberal_Democratic_Party_of_Moldova" title="Liberal Democratic Party of Moldova">Liberal Democratic</a>
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/6/64/Flag_of_Montenegro.svg/23px-Flag_of_Montenegro.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/6/64/Flag_of_Montenegro.svg/35px-Flag_of_Montenegro.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/6/64/Flag_of_Montenegro.svg/46px-Flag_of_Montenegro.svg.png 2x" data-file-width="640" data-file-height="320">&nbsp;</span>Montenegro
</td>
<td>4 years
</td>
<td><a href="/wiki/2016_Montenegrin_parliamentary_election" title="2016 Montenegrin parliamentary election"><span data-sort-value="000000002016-10-16-0000" style="white-space:nowrap">16 October 2016</span></a>
</td>
<td><span data-sort-value="000000002020-10-01-0000" style="white-space:nowrap">October 2020</span>
</td>
<td>5 years
</td>
<td><a href="/wiki/2018_Montenegrin_presidential_election" title="2018 Montenegrin presidential election"><span data-sort-value="000000002018-04-15-0000" style="white-space:nowrap">15 April 2018</span></a>
</td>
<td><span data-sort-value="000000002023-01-01-0000" style="white-space:nowrap">2023</span>
</td>
<td><a href="/wiki/Dominant-party_system" title="Dominant-party system">Dominant-party system</a>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/2/20/Flag_of_the_Netherlands.svg/23px-Flag_of_the_Netherlands.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/2/20/Flag_of_the_Netherlands.svg/35px-Flag_of_the_Netherlands.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/2/20/Flag_of_the_Netherlands.svg/45px-Flag_of_the_Netherlands.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Netherlands
</td>
<td>4 years
</td>
<td><a href="/wiki/2017_Dutch_general_election" title="2017 Dutch general election"><span data-sort-value="000000002017-03-15-0000" style="white-space:nowrap">15 March 2017</span></a>
</td>
<td><a href="/wiki/Next_Dutch_general_election" title="Next Dutch general election"><span data-sort-value="000000002021-03-01-0000" style="white-space:nowrap">March 2021</span></a>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_the_Netherlands" class="mw-redirect" title="Demographics of the Netherlands">17.1</a>
</td>
<td><a href="/wiki/Economy_of_the_Netherlands" title="Economy of the Netherlands">836</a>
</td>
<td>.857
</td>
<td><a href="/wiki/People%27s_Party_for_Freedom_and_Democracy" title="People's Party for Freedom and Democracy">VVD</a>, <a href="/wiki/Christian_Democratic_Appeal" title="Christian Democratic Appeal">CDA</a>, <a href="/wiki/Democrats_66" title="Democrats 66">D66</a>, <a href="/wiki/Christian_Union_(Netherlands)" title="Christian Union (Netherlands)">CU</a>
</td>
<td>Majority Coalition
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Flag_of_Norway.svg/21px-Flag_of_Norway.svg.png" decoding="async" width="21" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Flag_of_Norway.svg/32px-Flag_of_Norway.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Flag_of_Norway.svg/41px-Flag_of_Norway.svg.png 2x" data-file-width="1100" data-file-height="800">&nbsp;</span>Norway
</td>
<td>4 years
</td>
<td><a href="/wiki/2017_Norwegian_parliamentary_election" title="2017 Norwegian parliamentary election"><span data-sort-value="000000002017-09-11-0000" style="white-space:nowrap">11 September 2017</span></a>
</td>
<td><a href="/wiki/2021_Norwegian_parliamentary_election" title="2021 Norwegian parliamentary election"><span data-sort-value="000000002021-09-01-0000" style="white-space:nowrap">September 2021</span></a>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Norway" title="Demographics of Norway">5.2</a>
</td>
<td><a href="/wiki/Economy_of_Norway" title="Economy of Norway">483</a>
</td>
<td>.894
</td>
<td><a href="/wiki/Conservative_Party_(Norway)" title="Conservative Party (Norway)">Conservative</a>, <a href="/wiki/Progress_Party_(Norway)" title="Progress Party (Norway)">Progress</a>, <a href="/wiki/Liberal_Party_(Norway)" title="Liberal Party (Norway)">Venstre</a>
</td>
<td>Minority Coalition; confidence from <a href="/wiki/Christian_Democratic_Party_(Norway)" title="Christian Democratic Party (Norway)">KrF</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/en/thumb/1/12/Flag_of_Poland.svg/23px-Flag_of_Poland.svg.png" decoding="async" width="23" height="14" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/en/thumb/1/12/Flag_of_Poland.svg/35px-Flag_of_Poland.svg.png 1.5x, //upload.wikimedia.org/wikipedia/en/thumb/1/12/Flag_of_Poland.svg/46px-Flag_of_Poland.svg.png 2x" data-file-width="1280" data-file-height="800">&nbsp;</span>Poland
</td>
<td>4 years
</td>
<td><a href="/wiki/2015_Polish_parliamentary_election" title="2015 Polish parliamentary election"><span data-sort-value="000000002015-10-25-0000" style="white-space:nowrap">25 October 2015</span></a>
</td>
<td><a href="/wiki/Next_Polish_parliamentary_election" class="mw-redirect" title="Next Polish parliamentary election"><span data-sort-value="000000002019-11-01-0000" style="white-space:nowrap">November 2019</span></a>
</td>
<td>5 years
</td>
<td><a href="/wiki/2015_Polish_presidential_election" title="2015 Polish presidential election"><span data-sort-value="000000002015-05-10-0000" style="white-space:nowrap">10 May 2015</span></a>
</td>
<td><a href="/wiki/2020_Polish_presidential_election" title="2020 Polish presidential election"><span data-sort-value="000000002020-04-01-0000" style="white-space:nowrap">April 2020</span></a>
</td>
<td>
</td>
<td><a href="/wiki/Demography_of_Poland" class="mw-redirect" title="Demography of Poland">38.5</a>
</td>
<td><a href="/wiki/Economy_of_Poland" title="Economy of Poland">614</a>
</td>
<td>.774
</td>
<td><i><a href="/wiki/Andrzej_Duda" title="Andrzej Duda">Andrzej Duda</a></i>
<p><a href="/wiki/Law_and_Justice" title="Law and Justice">PiS</a>
</p>
</td>
<td>Majority
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Flag_of_Portugal.svg/23px-Flag_of_Portugal.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Flag_of_Portugal.svg/35px-Flag_of_Portugal.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Flag_of_Portugal.svg/45px-Flag_of_Portugal.svg.png 2x" data-file-width="600" data-file-height="400">&nbsp;</span>Portugal
</td>
<td>4 years
</td>
<td><a href="/wiki/2015_Portuguese_legislative_election" title="2015 Portuguese legislative election"><span data-sort-value="000000002015-10-04-0000" style="white-space:nowrap">4 October 2015</span></a>
</td>
<td><a href="/wiki/Next_Portuguese_legislative_election" class="mw-redirect" title="Next Portuguese legislative election"><span data-sort-value="000000002019-10-06-0000" style="white-space:nowrap">6 October 2019</span></a>
</td>
<td>5 years
</td>
<td><a href="/wiki/2016_Portuguese_presidential_election" title="2016 Portuguese presidential election"><span data-sort-value="000000002016-01-24-0000" style="white-space:nowrap">24 January 2016</span></a>
</td>
<td><a href="/wiki/2021_Portuguese_presidential_election" title="2021 Portuguese presidential election"><span data-sort-value="000000002021-01-01-0000" style="white-space:nowrap">January 2021</span></a>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Portugal" title="Demographics of Portugal">10.3</a>
</td>
<td><a href="/wiki/Economy_of_Portugal" title="Economy of Portugal">238</a>
</td>
<td>.732
</td>
<td><a href="/wiki/Socialist_Party_(Portugal)" title="Socialist Party (Portugal)">PS</a>
</td>
<td>Minority; confidence from <a href="/wiki/Left_Bloc" title="Left Bloc">BE</a>, <a href="/wiki/Portuguese_Communist_Party" title="Portuguese Communist Party">PCP</a>, <a href="/wiki/Ecologist_Party_%22The_Greens%22" title="Ecologist Party &quot;The Greens&quot;">PEV</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/7/73/Flag_of_Romania.svg/23px-Flag_of_Romania.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/7/73/Flag_of_Romania.svg/35px-Flag_of_Romania.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/7/73/Flag_of_Romania.svg/45px-Flag_of_Romania.svg.png 2x" data-file-width="600" data-file-height="400">&nbsp;</span>Romania
</td>
<td>4 years<sup id="cite_ref-22" class="reference"><a href="#cite_note-22">[22]</a></sup>
</td>
<td><a href="/wiki/2016_Romanian_legislative_election" title="2016 Romanian legislative election"><span data-sort-value="000000002016-12-11-0000" style="white-space:nowrap">11 December 2016</span></a>
</td>
<td><a href="/wiki/Next_Romanian_legislative_election" title="Next Romanian legislative election"><span data-sort-value="000000002020-12-01-0000" style="white-space:nowrap">December 2020</span></a>
</td>
<td>5 years
</td>
<td><a href="/wiki/2014_Romanian_presidential_election" title="2014 Romanian presidential election"><span data-sort-value="000000002014-11-02-0000" style="white-space:nowrap">2 November 2014</span></a>
</td>
<td><a href="/wiki/2019_Romanian_presidential_election" title="2019 Romanian presidential election"><span data-sort-value="000000002019-11-01-0000" style="white-space:nowrap">November 2019</span></a>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Romania" title="Demographics of Romania">20.1</a>
</td>
<td><a href="/wiki/Economy_of_Romania" title="Economy of Romania">187</a>
</td>
<td>.687
</td>
<td><a href="/wiki/Social_Democratic_Party_(Romania)" title="Social Democratic Party (Romania)">PSD</a>, <a href="/wiki/Alliance_of_Liberals_and_Democrats_(Romania)" title="Alliance of Liberals and Democrats (Romania)">ALDE</a>
</td>
<td>Majority coalition, although it is supported by <a href="/wiki/Democratic_Union_of_Hungarians_in_Romania" class="mw-redirect" title="Democratic Union of Hungarians in Romania">UDMR</a>.
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/en/thumb/f/f3/Flag_of_Russia.svg/23px-Flag_of_Russia.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/en/thumb/f/f3/Flag_of_Russia.svg/35px-Flag_of_Russia.svg.png 1.5x, //upload.wikimedia.org/wikipedia/en/thumb/f/f3/Flag_of_Russia.svg/45px-Flag_of_Russia.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Russia
</td>
<td>5 years
</td>
<td><a href="/wiki/2016_Russian_legislative_election" title="2016 Russian legislative election"><span data-sort-value="000000002016-09-18-0000" style="white-space:nowrap">18 September 2016</span></a>
</td>
<td><a href="/wiki/2021_Russian_legislative_election" title="2021 Russian legislative election"><span data-sort-value="000000002021-09-01-0000" style="white-space:nowrap">September 2021</span></a>
</td>
<td>6 years
</td>
<td><a href="/wiki/2018_Russian_presidential_election" title="2018 Russian presidential election"><span data-sort-value="000000002018-03-18-0000" style="white-space:nowrap">18 March 2018</span></a>
</td>
<td><a href="/wiki/2024_Russian_presidential_election" title="2024 Russian presidential election"><span data-sort-value="000000002024-03-01-0000" style="white-space:nowrap">March 2024</span></a>
</td>
<td><a href="/wiki/2018_Russian_presidential_election#Reaction" title="2018 Russian presidential election">Disputed</a>
</td>
<td><a href="/wiki/Demography_of_Russia" class="mw-redirect" title="Demography of Russia">143.4</a>
</td>
<td><a href="/wiki/Economy_of_Russia" title="Economy of Russia">1,858</a>
</td>
<td>.670<sup id="cite_ref-UN2011_9-2" class="reference"><a href="#cite_note-UN2011-9">[9]</a></sup>
</td>
<td><i><a href="/wiki/Vladimir_Putin" title="Vladimir Putin">Vladimir Putin</a></i>,
<p><a href="/wiki/United_Russia" title="United Russia">United Russia</a>
</p>
</td>
<td>Majority
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/b/b1/Flag_of_San_Marino.svg/20px-Flag_of_San_Marino.svg.png" decoding="async" width="20" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/b/b1/Flag_of_San_Marino.svg/31px-Flag_of_San_Marino.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/b/b1/Flag_of_San_Marino.svg/40px-Flag_of_San_Marino.svg.png 2x" data-file-width="800" data-file-height="600">&nbsp;</span>San Marino
</td>
<td>5 years
</td>
<td><a href="/wiki/2016_Sammarinese_general_election" title="2016 Sammarinese general election"><span data-sort-value="000000002016-11-20-0000" style="white-space:nowrap">20 November 2016</span></a>
</td>
<td><span data-sort-value="000000002021-11-01-0000" style="white-space:nowrap">November 2021</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/f/ff/Flag_of_Serbia.svg/23px-Flag_of_Serbia.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/f/ff/Flag_of_Serbia.svg/35px-Flag_of_Serbia.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/f/ff/Flag_of_Serbia.svg/45px-Flag_of_Serbia.svg.png 2x" data-file-width="945" data-file-height="630">&nbsp;</span>Serbia
</td>
<td>5 years
</td>
<td><a href="/wiki/2016_Serbian_parliamentary_election" title="2016 Serbian parliamentary election"><span data-sort-value="000000002016-04-24-0000" style="white-space:nowrap">24 April 2016</span></a>
</td>
<td><a href="/wiki/Next_Serbian_parliamentary_election" title="Next Serbian parliamentary election"><span data-sort-value="000000002020-04-01-0000" style="white-space:nowrap">April 2020</span></a>
</td>
<td>5 years
</td>
<td><a href="/wiki/2017_Serbian_presidential_election" title="2017 Serbian presidential election"><span data-sort-value="000000002017-04-02-0000" style="white-space:nowrap">2 April 2017</span></a>
</td>
<td><span data-sort-value="000000002022-01-01-0000" style="white-space:nowrap">2022</span>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Serbia" title="Demographics of Serbia">7.1</a>
</td>
<td><a href="/wiki/Economy_of_Serbia" title="Economy of Serbia">53</a>
</td>
<td>.696
</td>
<td><a href="/wiki/Serbian_Progressive_Party" title="Serbian Progressive Party">SNS</a>
</td>
<td>Majority
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Flag_of_Slovakia.svg/23px-Flag_of_Slovakia.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Flag_of_Slovakia.svg/35px-Flag_of_Slovakia.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Flag_of_Slovakia.svg/45px-Flag_of_Slovakia.svg.png 2x" data-file-width="900" data-file-height="600">&nbsp;</span>Slovakia
</td>
<td>4 years
</td>
<td><a href="/wiki/2016_Slovak_parliamentary_election" title="2016 Slovak parliamentary election"><span data-sort-value="000000002016-03-05-0000" style="white-space:nowrap">5 March 2016</span></a>
</td>
<td><a href="/wiki/Next_Slovak_parliamentary_election" title="Next Slovak parliamentary election"><span data-sort-value="000000002020-03-01-0000" style="white-space:nowrap">March 2020</span></a>
</td>
<td>5 years
</td>
<td><a href="/wiki/2019_Slovak_presidential_election" title="2019 Slovak presidential election"><span data-sort-value="000000002019-03-16-0000" style="white-space:nowrap">16 March 2019</span></a>
</td>
<td><span data-sort-value="000000002024-01-01-0000" style="white-space:nowrap">2024</span>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Slovakia" title="Demographics of Slovakia">5.4</a>
</td>
<td><a href="/wiki/Economy_of_Slovakia" title="Economy of Slovakia">91</a>
</td>
<td>.788
</td>
<td><a href="/wiki/Direction_%E2%80%93_Social_Democracy" title="Direction – Social Democracy">Direction – Social Democracy</a>
</td>
<td>Coalition with <a href="/wiki/Slovak_National_Party" title="Slovak National Party">SNS</a> and <a href="/wiki/Most%E2%80%93H%C3%ADd" title="Most–Híd">Most–Híd</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/f/f0/Flag_of_Slovenia.svg/23px-Flag_of_Slovenia.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/f/f0/Flag_of_Slovenia.svg/35px-Flag_of_Slovenia.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/f/f0/Flag_of_Slovenia.svg/46px-Flag_of_Slovenia.svg.png 2x" data-file-width="1200" data-file-height="600">&nbsp;</span>Slovenia
</td>
<td>4 years
</td>
<td><a href="/wiki/2018_Slovenian_parliamentary_election" title="2018 Slovenian parliamentary election"><span data-sort-value="000000002018-06-03-0000" style="white-space:nowrap">3 June 2018</span></a>
</td>
<td><span data-sort-value="000000002022-06-01-0000" style="white-space:nowrap">June 2022</span>
</td>
<td>5 years
</td>
<td><a href="/wiki/2017_Slovenian_presidential_election" title="2017 Slovenian presidential election"><span data-sort-value="000000002017-10-22-0000" style="white-space:nowrap">22 October 2017</span></a>
</td>
<td><span data-sort-value="000000002022-01-01-0000" style="white-space:nowrap">2022</span>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Slovenia" title="Demographics of Slovenia">2.1</a>
</td>
<td><a href="/wiki/Economy_of_Slovenia" title="Economy of Slovenia">45</a>
</td>
<td>.840
</td>
<td><a href="/w/index.php?title=Party_of_modern_centre_SMC&amp;action=edit&amp;redlink=1" class="new" title="Party of modern centre SMC (page does not exist)">Party of modern centre SMC</a>/<a href="/wiki/Social_Democrats_(Slovenia)" title="Social Democrats (Slovenia)">Social Democrat</a>
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/en/thumb/9/9a/Flag_of_Spain.svg/23px-Flag_of_Spain.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/en/thumb/9/9a/Flag_of_Spain.svg/35px-Flag_of_Spain.svg.png 1.5x, //upload.wikimedia.org/wikipedia/en/thumb/9/9a/Flag_of_Spain.svg/45px-Flag_of_Spain.svg.png 2x" data-file-width="750" data-file-height="500">&nbsp;</span>Spain
</td>
<td>4 years<sup id="cite_ref-23" class="reference"><a href="#cite_note-23">[23]</a></sup>
</td>
<td><a href="/wiki/2019_Spanish_general_election" title="2019 Spanish general election"><span data-sort-value="000000002019-04-28-0000" style="white-space:nowrap">28 April 2019</span></a>
</td>
<td><a href="/wiki/Next_Spanish_general_election" title="Next Spanish general election">May 2023</a>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>
</td>
<td><a href="/wiki/Demography_of_Spain" class="mw-redirect" title="Demography of Spain">46.7</a>
</td>
<td><a href="/wiki/Economy_of_Spain" title="Economy of Spain">1,478</a>
</td>
<td>.796
</td>
<td><a href="/wiki/Spanish_Socialist_Workers%27_Party" title="Spanish Socialist Workers' Party">Spanish Socialist Workers' Party</a>
</td>
<td>Minority Coalition; confidence from <a href="/wiki/Podemos_(Spanish_political_party)" title="Podemos (Spanish political party)">Podemos</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/en/thumb/4/4c/Flag_of_Sweden.svg/23px-Flag_of_Sweden.svg.png" decoding="async" width="23" height="14" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/en/thumb/4/4c/Flag_of_Sweden.svg/35px-Flag_of_Sweden.svg.png 1.5x, //upload.wikimedia.org/wikipedia/en/thumb/4/4c/Flag_of_Sweden.svg/46px-Flag_of_Sweden.svg.png 2x" data-file-width="1600" data-file-height="1000">&nbsp;</span>Sweden
</td>
<td>4 years
</td>
<td><a href="/wiki/2018_Swedish_general_election" title="2018 Swedish general election"><span data-sort-value="000000002018-09-09-0000" style="white-space:nowrap">9 September 2018</span></a>
</td>
<td><a href="/wiki/2022_Swedish_general_election" title="2022 Swedish general election"><span data-sort-value="000000002022-09-11-0000" style="white-space:nowrap">11 September 2022</span></a>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Sweden" title="Demographics of Sweden">9.6</a>
</td>
<td><a href="/wiki/Economy_of_Sweden" title="Economy of Sweden">539</a>
</td>
<td>.859
</td>
<td><a href="/wiki/Swedish_Social_Democratic_Party" title="Swedish Social Democratic Party">Social Democratic</a>/<a href="/wiki/Green_Party_(Sweden)" title="Green Party (Sweden)">Green</a>
</td>
<td>Minority Coalition; confidence from the <a href="/wiki/Centre_Party_(Sweden)" title="Centre Party (Sweden)">Center Party</a> and the <a href="/wiki/Liberals_(Sweden)" title="Liberals (Sweden)">Liberals</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Flag_of_Switzerland.svg/16px-Flag_of_Switzerland.svg.png" decoding="async" width="16" height="16" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Flag_of_Switzerland.svg/24px-Flag_of_Switzerland.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Flag_of_Switzerland.svg/32px-Flag_of_Switzerland.svg.png 2x" data-file-width="1000" data-file-height="1000">&nbsp;&nbsp;</span>Switzerland
</td>
<td>4 years
</td>
<td><a href="/wiki/2015_Swiss_federal_election" title="2015 Swiss federal election"><span data-sort-value="000000002015-10-18-0000" style="white-space:nowrap">18 October 2015</span></a>
</td>
<td><a href="/wiki/2019_Swiss_federal_election" title="2019 Swiss federal election"><span data-sort-value="000000002019-10-20-0000" style="white-space:nowrap">20 October 2019</span></a>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Switzerland" title="Demographics of Switzerland">8.0</a>
</td>
<td><a href="/wiki/Economy_of_Switzerland" title="Economy of Switzerland">632</a>
</td>
<td>.849
</td>
<td>see <a href="/wiki/Swiss_Federal_Council" class="mw-redirect" title="Swiss Federal Council">Swiss Federal Council</a>
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/4/49/Flag_of_Ukraine.svg/23px-Flag_of_Ukraine.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/4/49/Flag_of_Ukraine.svg/35px-Flag_of_Ukraine.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/4/49/Flag_of_Ukraine.svg/45px-Flag_of_Ukraine.svg.png 2x" data-file-width="1200" data-file-height="800">&nbsp;</span>Ukraine
</td>
<td>5 years
</td>
<td><a href="/wiki/2014_Ukrainian_parliamentary_election" title="2014 Ukrainian parliamentary election"><span data-sort-value="000000002014-10-26-0000" style="white-space:nowrap">26 October 2014</span></a>
</td>
<td><a href="/wiki/2019_Ukrainian_parliamentary_election" title="2019 Ukrainian parliamentary election"><span data-sort-value="000000002019-07-21-0000" style="white-space:nowrap">21 July 2019</span></a>
</td>
<td>5 years
</td>
<td><a href="/wiki/2019_Ukrainian_presidential_election" title="2019 Ukrainian presidential election"><span data-sort-value="000000002019-03-31-0000" style="white-space:nowrap">31 March 2019</span></a>
</td>
<td><span data-sort-value="000000002024-01-01-0000" style="white-space:nowrap">2024</span>
</td>
<td>Disputed, Dominant-party system
</td>
<td><a href="/wiki/Demographics_of_Ukraine" title="Demographics of Ukraine">44.8</a>
</td>
<td><a href="/wiki/Economy_of_Ukraine" title="Economy of Ukraine">180</a>
</td>
<td>.672
</td>
<td><a href="/wiki/Petro_Poroshenko_Bloc_%22Solidarity%22" class="mw-redirect" title="Petro Poroshenko Bloc &quot;Solidarity&quot;">Petro Poroshenko Bloc "Solidarity"</a>/<a href="/wiki/People%27s_Front_(Ukraine)" title="People's Front (Ukraine)">People's Front</a>
</td>
<td>Majority coalition
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/en/thumb/a/ae/Flag_of_the_United_Kingdom.svg/23px-Flag_of_the_United_Kingdom.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/en/thumb/a/ae/Flag_of_the_United_Kingdom.svg/35px-Flag_of_the_United_Kingdom.svg.png 1.5x, //upload.wikimedia.org/wikipedia/en/thumb/a/ae/Flag_of_the_United_Kingdom.svg/46px-Flag_of_the_United_Kingdom.svg.png 2x" data-file-width="1200" data-file-height="600">&nbsp;</span>United Kingdom
</td>
<td>5 years<sup id="cite_ref-24" class="reference"><a href="#cite_note-24">[24]</a></sup>
</td>
<td><a href="/wiki/2017_United_Kingdom_general_election" title="2017 United Kingdom general election"><span data-sort-value="000000002017-06-08-0000" style="white-space:nowrap">8 June 2017</span></a>
</td>
<td><a href="/w/index.php?title=2022_United_Kingdom_general_election&amp;action=edit&amp;redlink=1" class="new" title="2022 United Kingdom general election (page does not exist)"><span data-sort-value="000000002022-05-01-0000" style="white-space:nowrap">May 2022</span></a>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>
</td>
<td><a href="/wiki/Demography_of_the_United_Kingdom" title="Demography of the United Kingdom">63.7</a>
</td>
<td><a href="/wiki/Economy_of_the_United_Kingdom" title="Economy of the United Kingdom">2,429</a>
</td>
<td>.802
</td>
<td><a href="/wiki/Conservative_Party_(UK)" title="Conservative Party (UK)">Conservative</a>
</td>
<td>Minority (Confidence and supply arrangement with the <a href="/wiki/Democratic_Unionist_Party" title="Democratic Unionist Party">DUP</a>)
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Flag_of_Europe.svg/23px-Flag_of_Europe.svg.png" decoding="async" width="23" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Flag_of_Europe.svg/35px-Flag_of_Europe.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Flag_of_Europe.svg/45px-Flag_of_Europe.svg.png 2x" data-file-width="810" data-file-height="540">&nbsp;</span>European Union
</td>
<td>5 years
</td>
<td><a href="/wiki/2019_European_Parliament_election" title="2019 European Parliament election"><span data-sort-value="000000002019-05-23-0000" style="white-space:nowrap">23 May 2019</span></a>
</td>
<td><span data-sort-value="000000002024-05-01-0000" style="white-space:nowrap">May 2024</span>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_the_European_Union" title="Demographics of the European Union">507.9</a>
</td>
<td><a href="/wiki/Economy_of_the_European_Union" title="Economy of the European Union">17,577</a>
</td>
<td>no data
</td>
<td>
</td>
<td><a href="/wiki/European_People%27s_Party_Group" class="mw-redirect" title="European People's Party Group">EPP</a>, <a href="/wiki/Progressive_Alliance_of_Socialists_and_Democrats" title="Progressive Alliance of Socialists and Democrats">S&amp;D</a>, <a href="/wiki/Alliance_of_Liberals_and_Democrats_for_Europe_Group" class="mw-redirect" title="Alliance of Liberals and Democrats for Europe Group">ALDE</a> (informal alliance in the <a href="/wiki/European_Parliament" title="European Parliament">EP</a>)
</td></tr></tbody><tfoot></tfoot></table>
<table class="wikitable sortable jquery-tablesorter" style="font-size:90%;">
<thead><tr>
<th rowspan="2" class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">Country
</th>
<th colspan="3">Parliamentary election
</th>
<th colspan="3">Presidential election
</th>
<th rowspan="2" class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending"><a href="/wiki/Unfair_election" title="Unfair election">Fairness</a>
</th>
<th rowspan="2" class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending"><a href="/wiki/List_of_countries_by_population" class="mw-redirect" title="List of countries by population">Pop.</a><br>(m)
</th>
<th rowspan="2" class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending"><a href="/wiki/List_of_countries_by_GDP_(nominal)" title="List of countries by GDP (nominal)">GDP</a><br>($bn)
</th>
<th rowspan="2" class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending"><a href="/wiki/List_of_countries_by_inequality-adjusted_HDI" title="List of countries by inequality-adjusted HDI">IHDI</a>
</th>
<th rowspan="2" class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">In power now
</th></tr><tr>
<th class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">Term
</th>
<th class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">Last election
</th>
<th class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">Next election
</th>
<th class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">Term
</th>
<th class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">Last election
</th>
<th class="headerSort" tabindex="0" role="columnheader button" title="Sort ascending">Next election
</th></tr></thead><tbody>

<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/8/88/Flag_of_Australia_%28converted%29.svg/23px-Flag_of_Australia_%28converted%29.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/8/88/Flag_of_Australia_%28converted%29.svg/35px-Flag_of_Australia_%28converted%29.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/8/88/Flag_of_Australia_%28converted%29.svg/46px-Flag_of_Australia_%28converted%29.svg.png 2x" data-file-width="1280" data-file-height="640">&nbsp;</span>Australia
</td>
<td>3 years<sup id="cite_ref-25" class="reference"><a href="#cite_note-25">[25]</a></sup>
</td>
<td><a href="/wiki/2019_Australian_federal_election" title="2019 Australian federal election"><span data-sort-value="000000002019-05-18-0000" style="white-space:nowrap">18 May 2019</span></a>
</td>
<td><span data-sort-value="000000002022-01-01-0000" style="white-space:nowrap">2022</span>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Australia" class="mw-redirect" title="Demographics of Australia">24.1</a>
</td>
<td><a href="/wiki/Economy_of_Australia" title="Economy of Australia">1,620</a>
</td>
<td>.858
</td>
<td><a href="/wiki/Coalition_(Australia)" title="Coalition (Australia)">Liberal/National</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/3/35/Flag_of_the_Cook_Islands.svg/23px-Flag_of_the_Cook_Islands.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/3/35/Flag_of_the_Cook_Islands.svg/35px-Flag_of_the_Cook_Islands.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/3/35/Flag_of_the_Cook_Islands.svg/46px-Flag_of_the_Cook_Islands.svg.png 2x" data-file-width="600" data-file-height="300">&nbsp;</span>Cook Islands
</td>
<td>4 years
</td>
<td><a href="/wiki/2018_Cook_Islands_general_election" title="2018 Cook Islands general election"><span data-sort-value="000000002018-06-14-0000" style="white-space:nowrap">14 June 2018</span></a>
</td>
<td><a href="/wiki/Next_Cook_Islands_general_election" class="mw-redirect" title="Next Cook Islands general election"><span data-sort-value="000000002022-04-01-0000" style="white-space:nowrap">April 2022</span></a>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/Cook_Islands_Party" title="Cook Islands Party">Cook Islands Party</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Flag_of_the_Federated_States_of_Micronesia.svg/23px-Flag_of_the_Federated_States_of_Micronesia.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Flag_of_the_Federated_States_of_Micronesia.svg/35px-Flag_of_the_Federated_States_of_Micronesia.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Flag_of_the_Federated_States_of_Micronesia.svg/46px-Flag_of_the_Federated_States_of_Micronesia.svg.png 2x" data-file-width="760" data-file-height="400">&nbsp;</span>Federated States of Micronesia
</td>
<td>2 years
</td>
<td><a href="/wiki/2019_Micronesian_parliamentary_election" title="2019 Micronesian parliamentary election"><span data-sort-value="000000002019-03-05-0000" style="white-space:nowrap">5 March 2019</span></a>
</td>
<td><span data-sort-value="000000002021-03-01-0000" style="white-space:nowrap">March 2021</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Flag_of_Fiji.svg/23px-Flag_of_Fiji.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Flag_of_Fiji.svg/35px-Flag_of_Fiji.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Flag_of_Fiji.svg/46px-Flag_of_Fiji.svg.png 2x" data-file-width="1200" data-file-height="600">&nbsp;</span>Fiji
</td>
<td>4 years
</td>
<td><a href="/wiki/2018_Fijian_general_election" title="2018 Fijian general election"><span data-sort-value="000000002018-11-14-0000" style="white-space:nowrap">14 November 2018</span></a>
</td>
<td><span data-sort-value="000000002022-11-01-0000" style="white-space:nowrap">November 2022</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/FijiFirst" title="FijiFirst">FijiFirst</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Flag_of_Kiribati.svg/23px-Flag_of_Kiribati.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Flag_of_Kiribati.svg/35px-Flag_of_Kiribati.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Flag_of_Kiribati.svg/46px-Flag_of_Kiribati.svg.png 2x" data-file-width="600" data-file-height="300">&nbsp;</span>Kiribati
</td>
<td>4 years
</td>
<td><a href="/wiki/Kiribati_parliamentary_election,_2015%E2%80%9316" class="mw-redirect" title="Kiribati parliamentary election, 2015–16"><span data-sort-value="000000002015-12-30-0000" style="white-space:nowrap">30 December 2015</span></a>
</td>
<td><a href="/w/index.php?title=Next_Kiribati_parliamentary_election&amp;action=edit&amp;redlink=1" class="new" title="Next Kiribati parliamentary election (page does not exist)"><span data-sort-value="000000002019-12-01-0000" style="white-space:nowrap">December 2019</span></a>
</td>
<td>
</td>
<td><a href="/wiki/2016_Kiribati_presidential_election" title="2016 Kiribati presidential election"><span data-sort-value="000000002016-03-09-0000" style="white-space:nowrap">9 March 2016</span></a>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td><i>awaiting results</i>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Flag_of_the_Marshall_Islands.svg/23px-Flag_of_the_Marshall_Islands.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Flag_of_the_Marshall_Islands.svg/35px-Flag_of_the_Marshall_Islands.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Flag_of_the_Marshall_Islands.svg/46px-Flag_of_the_Marshall_Islands.svg.png 2x" data-file-width="570" data-file-height="300">&nbsp;</span>Marshall Islands
</td>
<td>4 years
</td>
<td><a href="/wiki/2015_Marshallese_general_election" title="2015 Marshallese general election"><span data-sort-value="000000002015-11-16-0000" style="white-space:nowrap">16 November 2015</span></a>
</td>
<td><span data-sort-value="000000002019-11-01-0000" style="white-space:nowrap">November 2019</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/3/30/Flag_of_Nauru.svg/23px-Flag_of_Nauru.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/3/30/Flag_of_Nauru.svg/35px-Flag_of_Nauru.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/3/30/Flag_of_Nauru.svg/46px-Flag_of_Nauru.svg.png 2x" data-file-width="600" data-file-height="300">&nbsp;</span>Nauru
</td>
<td>3 years
</td>
<td><a href="/wiki/2016_Nauruan_parliamentary_election" title="2016 Nauruan parliamentary election"><span data-sort-value="000000002016-07-09-0000" style="white-space:nowrap">9 July 2016</span></a>
</td>
<td><a href="/w/index.php?title=Next_Nauruan_parliamentary_election&amp;action=edit&amp;redlink=1" class="new" title="Next Nauruan parliamentary election (page does not exist)"><span data-sort-value="000000002019-07-01-0000" style="white-space:nowrap">July 2019</span></a>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>(no political parties)
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Flag_of_New_Zealand.svg/23px-Flag_of_New_Zealand.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Flag_of_New_Zealand.svg/35px-Flag_of_New_Zealand.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Flag_of_New_Zealand.svg/46px-Flag_of_New_Zealand.svg.png 2x" data-file-width="1200" data-file-height="600">&nbsp;</span>New Zealand
</td>
<td>3 years
</td>
<td><a href="/wiki/2017_New_Zealand_general_election" title="2017 New Zealand general election"><span data-sort-value="000000002017-09-23-0000" style="white-space:nowrap">23 September 2017</span></a>
</td>
<td><a href="/wiki/Next_New_Zealand_general_election" title="Next New Zealand general election"><span data-sort-value="000000002020-09-01-0000" style="white-space:nowrap">September 2020</span></a>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_New_Zealand" title="Demographics of New Zealand">4.3</a>
</td>
<td><a href="/wiki/Economy_of_New_Zealand" title="Economy of New Zealand">161</a>
</td>
<td>no data
</td>
<td>Labour/NZ First/Greens
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/0/01/Flag_of_Niue.svg/23px-Flag_of_Niue.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/0/01/Flag_of_Niue.svg/35px-Flag_of_Niue.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/0/01/Flag_of_Niue.svg/46px-Flag_of_Niue.svg.png 2x" data-file-width="600" data-file-height="300">&nbsp;</span>Niue
</td>
<td>3 years
</td>
<td><a href="/wiki/2017_Niuean_general_election" title="2017 Niuean general election"><span data-sort-value="000000002017-05-06-0000" style="white-space:nowrap">6 May 2017</span></a>
</td>
<td><span data-sort-value="000000002020-05-01-0000" style="white-space:nowrap">May 2020</span>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>(no political parties)
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/4/48/Flag_of_Palau.svg/23px-Flag_of_Palau.svg.png" decoding="async" width="23" height="14" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/4/48/Flag_of_Palau.svg/35px-Flag_of_Palau.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/4/48/Flag_of_Palau.svg/46px-Flag_of_Palau.svg.png 2x" data-file-width="800" data-file-height="500">&nbsp;</span>Palau
</td>
<td>4 years
</td>
<td><a href="/wiki/2016_Palauan_general_election" title="2016 Palauan general election"><span data-sort-value="000000002016-11-01-0000" style="white-space:nowrap">1 November 2016</span></a>
</td>
<td><span data-sort-value="000000002020-11-01-0000" style="white-space:nowrap">November 2020</span>
</td>
<td>4 years
</td>
<td><a href="/wiki/2016_Palauan_presidential_election" title="2016 Palauan presidential election"><span data-sort-value="000000002016-11-01-0000" style="white-space:nowrap">1 November 2016</span></a>
</td>
<td><span data-sort-value="000000002020-01-01-0000" style="white-space:nowrap">2020</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Flag_of_Papua_New_Guinea.svg/20px-Flag_of_Papua_New_Guinea.svg.png" decoding="async" width="20" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Flag_of_Papua_New_Guinea.svg/31px-Flag_of_Papua_New_Guinea.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Flag_of_Papua_New_Guinea.svg/40px-Flag_of_Papua_New_Guinea.svg.png 2x" data-file-width="600" data-file-height="450">&nbsp;</span>Papua New Guinea
</td>
<td>5 years
</td>
<td><a href="/wiki/2017_Papua_New_Guinean_general_election" title="2017 Papua New Guinean general election"><span data-sort-value="000000002017-06-24-0000" style="white-space:nowrap">24 June 2017</span></a>
</td>
<td><span data-sort-value="000000002022-07-01-0000" style="white-space:nowrap">July 2022</span>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>
</td>
<td><a href="/wiki/Demographics_of_Papua_New_Guinea" title="Demographics of Papua New Guinea">8.1</a>
</td>
<td><a href="/wiki/Economy_of_Papua_New_Guinea" title="Economy of Papua New Guinea">13</a>
</td>
<td>no data
</td>
<td><a href="/wiki/People%27s_National_Congress_Party" class="mw-redirect" title="People's National Congress Party">PNCP</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/3/31/Flag_of_Samoa.svg/23px-Flag_of_Samoa.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/3/31/Flag_of_Samoa.svg/35px-Flag_of_Samoa.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/3/31/Flag_of_Samoa.svg/46px-Flag_of_Samoa.svg.png 2x" data-file-width="2880" data-file-height="1440">&nbsp;</span>Samoa
</td>
<td>5 years
</td>
<td><a href="/wiki/2016_Samoan_general_election" title="2016 Samoan general election"><span data-sort-value="000000002016-03-04-0000" style="white-space:nowrap">4 March 2016</span></a>
</td>
<td><a href="/w/index.php?title=Next_Samoan_general_election&amp;action=edit&amp;redlink=1" class="new" title="Next Samoan general election (page does not exist)"><span data-sort-value="000000002021-03-01-0000" style="white-space:nowrap">March 2021</span></a>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/Human_Rights_Protection_Party" title="Human Rights Protection Party">HRPP</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/7/74/Flag_of_the_Solomon_Islands.svg/23px-Flag_of_the_Solomon_Islands.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/7/74/Flag_of_the_Solomon_Islands.svg/35px-Flag_of_the_Solomon_Islands.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/7/74/Flag_of_the_Solomon_Islands.svg/46px-Flag_of_the_Solomon_Islands.svg.png 2x" data-file-width="800" data-file-height="400">&nbsp;</span>Solomon Islands
</td>
<td>4 years
</td>
<td><a href="/wiki/2019_Solomon_Islands_general_election" title="2019 Solomon Islands general election"><span data-sort-value="000000002019-04-03-0000" style="white-space:nowrap">3 April 2019</span></a>
</td>
<td><span data-sort-value="000000002023-04-01-0000" style="white-space:nowrap">April 2023</span>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/Cabinet_of_the_Solomon_Islands" class="mw-redirect" title="Cabinet of the Solomon Islands">broad coalition</a>
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Flag_of_Tonga.svg/23px-Flag_of_Tonga.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Flag_of_Tonga.svg/35px-Flag_of_Tonga.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Flag_of_Tonga.svg/46px-Flag_of_Tonga.svg.png 2x" data-file-width="960" data-file-height="480">&nbsp;</span>Tonga
</td>
<td>4 years
</td>
<td><a href="/wiki/2017_Tongan_general_election" title="2017 Tongan general election"><span data-sort-value="000000002017-11-16-0000" style="white-space:nowrap">16 November 2017</span></a>
</td>
<td><span data-sort-value="000000002021-11-01-0000" style="white-space:nowrap">November 2021</span>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>(non-partisan)
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/3/38/Flag_of_Tuvalu.svg/23px-Flag_of_Tuvalu.svg.png" decoding="async" width="23" height="12" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/3/38/Flag_of_Tuvalu.svg/35px-Flag_of_Tuvalu.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/3/38/Flag_of_Tuvalu.svg/46px-Flag_of_Tuvalu.svg.png 2x" data-file-width="1200" data-file-height="600">&nbsp;</span>Tuvalu
</td>
<td>4 years
</td>
<td><a href="/wiki/2015_Tuvaluan_general_election" title="2015 Tuvaluan general election"><span data-sort-value="000000002015-03-31-0000" style="white-space:nowrap">31 March 2015</span></a>
</td>
<td><span data-sort-value="000000002019-01-01-0000" style="white-space:nowrap">2019</span>
</td>
<td colspan="3" data-sort-value="" style="background: #ececec; color: #2C2C2C; vertical-align: middle; font-size: smaller; text-align: center;" class="table-na">N/A
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>(no political parties)
</td></tr>
<tr>
<td><span class="flagicon"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Flag_of_Vanuatu.svg/23px-Flag_of_Vanuatu.svg.png" decoding="async" width="23" height="14" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Flag_of_Vanuatu.svg/35px-Flag_of_Vanuatu.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Flag_of_Vanuatu.svg/46px-Flag_of_Vanuatu.svg.png 2x" data-file-width="600" data-file-height="360">&nbsp;</span>Vanuatu
</td>
<td>4 years
</td>
<td><a href="/wiki/2016_Vanuatuan_general_election" title="2016 Vanuatuan general election"><span data-sort-value="000000002016-01-22-0000" style="white-space:nowrap">22 January 2016</span></a>
</td>
<td><a href="/wiki/Next_Vanuatuan_general_election" class="mw-redirect" title="Next Vanuatuan general election"><span data-sort-value="000000002020-01-01-0000" style="white-space:nowrap">January 2020</span></a>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td>
</td>
<td><a href="/wiki/Cabinet_of_Vanuatu" title="Cabinet of Vanuatu">broad coalition</a>
</td></tr></tbody><tfoot></tfoot></table>
"""