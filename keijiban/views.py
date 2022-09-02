from django.shortcuts import render
from django.http import HttpResponse
from keijiban.forms import KakikomiForm
import requests
import json
import pandas as pd
import xlsxwriter
import io

def kakikomi(request):
    f = KakikomiForm()
    if request.method == 'POST': # POSTの時だけ処理する
        f = KakikomiForm(request.POST) # POSTで送信した値をform変数に格納
        if f.is_valid(): # formの値が正当な時(バリデーションチェックを走らせる)
            y=int(f.data['year'])
            m=int(f.data['month'])
    # 空のデータベース作成
            df_MJW=pd.DataFrame()
    # 雑誌のデータをdataframe化
            journal=['NEJM',
             'JAMA',
             'LANCET',
             'Ann Intern Med',
             'CCM',
             'AJRCCM',
             'Chest',
             'BMJ',
             'J Trauma Acute Care Surg',
             'Intensive Care Med',
             'Critical Care',
             'JAMA Intern Med',
             'Clin Infect Dis',
             'Circulation',
             'Stroke'
             ]
            for_url=['N+Engl+J+Med',
            'JAMA',
            'Lancet',
            'Ann+Intern+Med',
            'Crit+Care+Med',
            'Am+J+Respir+Crit+Care+Med',
            'Chest',
            'BMJ',
            'J+Trauma+Acute+Care+Surg',
            'Intensive+Care+Med',
            'Crit+Care',
            'JAMA+Intern+Med',
            'Clin%20Infect%20Dis',
            'Circulation',
            'Stroke'
            ]
            HP=['http://nejm.org',
             'https://jamanetwork.com',
             'https://www.thelancet.com',
             'https://www.acpjournals.org/journal/aim',
             'https://journals.lww.com/ccmjournal',
             'https://www.atsjournals.org/journal/ajrccm',
             'https://journal.chestnet.org',
             'https://www.bmj.com',
             'https://journals.lww.com/jtrauma/',
             'https://www.springer.com/journal/134',
             'https://ccforum.biomedcentral.com',
             'https://jamanetwork.com/journals/jamainternalmedicine',
             'https://academic.oup.com/cid',
             'https://www.ahajournals.org/journal/circ',
             'https://www.ahajournals.org/journal/str'
             ]
            journals = pd.DataFrame(
                {'journal':journal,
                'for_url':for_url,
                'HP':HP}
                )
    
    # それぞれの雑誌をpubmed内で検索
            for i in range(len(journals)):
        # 特定の雑誌で期間内にpublishされた論文を抽出
                if m < 9:
                    url_search = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'\
                    'esearch.fcgi?db=pubmed&term=%22'+str(journals.iloc[i,1])+\
                    '%22%5BJournal%5D%29+AND+%28%28clinical+trial%5BPT%5D+OR+controlled+clinical+trial%5Bpt%5D+OR+guideline%5Bpt%5D+OR+meta-analysis%5BFpt%5D+OR+randomized+controlled+trial%5BPT%5D+OR+review%5BPT%5D+OR+systematic+review%5BFilter%5D%29%29&retmax=500&retmode=json&datetype=pdat'\
                        '&maxdate='+str(y)+'/0'+str(m+1)+'/01'\
                            '&mindate='+str(y)+'/0'+str(m)+'/01'
                elif m == 9:
                    url_search = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'\
                    'esearch.fcgi?db=pubmed&term=%22'+str(journals.iloc[i,1])+\
                    '%22%5BJournal%5D%29+AND+%28%28clinical+trial%5BPT%5D+OR+controlled+clinical+trial%5Bpt%5D+OR+guideline%5Bpt%5D+OR+meta-analysis%5BFpt%5D+OR+randomized+controlled+trial%5BPT%5D+OR+review%5BPT%5D+OR+systematic+review%5BFilter%5D%29%29&retmax=500&retmode=json&datetype=pdat'\
                        '&maxdate='+str(y)+'/10/01'\
                            '&mindate='+str(y)+'/09/01'
                else:
                    url_search = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'\
                    'esearch.fcgi?db=pubmed&term=%22'+str(journals.iloc[i,1])+\
                    '%22%5BJournal%5D%29+AND+%28%28clinical+trial%5BPT%5D+OR+controlled+clinical+trial%5Bpt%5D+OR+guideline%5Bpt%5D+OR+meta-analysis%5BFpt%5D+OR+randomized+controlled+trial%5BPT%5D+OR+review%5BPT%5D+OR+systematic+review%5BFilter%5D%29%29&retmax=500&retmode=json&datetype=pdat'\
                        '&maxdate='+str(y)+'/'+str(m+1)+'/01'\
                            '&mindate='+str(y)+'/'+str(m)+'/01'
                response = requests.get(url_search)
                response_json = response.json()

        # PMIDだけ取り出し
                pmids = response_json['esearchresult']['idlist']
        
        # PMIDからNIHのefetchを使って論文情報を抽出
                url_fetch = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=text&rettype=abstract&id='
                url_summary = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id='
                df_jour = pd.DataFrame()
                for pmid in pmids:
                    esponse = requests.get(url_fetch+pmid)
                    res_sum = requests.get(url_summary+pmid)
                    res_sum_json= res_sum.json()
                    series = pd.DataFrame(
                        data={'journal':[journals.iloc[i,0]],
                        'pmid':[pmid],
                        'title':res_sum_json['result'][pmid]['title'],
                        'abstract':[response.text],
                        'url':['https://pubmed.ncbi.nlm.nih.gov/'+pmid+'/'],
                        'HP':[journals.iloc[i,2]]
                        }
                    )
            # 論文をデータを雑誌ごとにまとめる
                    df_jour=pd.concat([df_jour, series], axis=0)

        # 雑誌ごとのデータをくっつけて完成
                df_MJW=pd.concat([df_MJW, df_jour],axis=0)

    # csvファイルに吐き出し
            output = io.BytesIO()
            writer = pd.ExcelWriter
            filename = str(y)+'_'+str(m)+'mjw_mini.xlsx'
            sheet_name = 'sheet1'
            df_MJW.to_excel(output,index=False,sheet_name=sheet_name)
            writer.close
            output.seek(0)
            response = HttpResponse(output, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=%s' % filename
            return response

    return render(request, 'keijiban/kakikomiform.html', {'form1': f})