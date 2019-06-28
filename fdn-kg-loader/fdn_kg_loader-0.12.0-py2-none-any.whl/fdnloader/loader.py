import pandas as pd
import os
from fdnloader.model import Brand, Product, Category, CategoryTree, CategorizedRel, ProducedRel
from fdnloader.store import Store
from fdnloader.filter import *
from glob import glob
import os
import pandas as pd


# TODO : add configure command

# TODO : automatic data splitting for brand
# TODO : automatic data splitting for product
# TODO : automatic data splitting for category
# TODO : automatic data splitting for distribution channel
# TODO : automatic splitting for relation
# TODO : automatic tagger for shade instead of variant by looking up to <has_shade> column




def load_file_chunk(base_path, path_pattern):
    # CURDIR = os.path.dirname(os.path.abspath('.'))
    # FDIR = os.path.join(CURDIR, 'fdn-annotator/shapeshift/reviews/*')
    # FDIR = os.path.join(CURDIR,'fdn-annotator/*reviews.csv')
    FDIR = os.path.join(base_path,path_pattern)
    files = [file for file in glob(FDIR)]

    N = len(files)

    df=[]
    for i in range(N):
        df0 = pd.read_csv(files[i])
        df.append(df0)
    df = pd.concat(df,sort=False)

    return df


def load_brand(df, xstore):
    df = df[['gid','name']]
    df = df.drop_duplicates()
    print(df)
    brands = df.to_dict(orient='record')
    for brand in brands:
        o = Brand()
        o.from_dict(brand)
        
        xstore.save(o)
    xstore.flush()



    #significant part start from here
    
        
def _load_undup_product(df,xstore):
    
    undup_df = df[df['name'].duplicated()==False]
#     undup_df = undup_df.head()
    prods = undup_df.to_dict(orient='record')
    try:
        for prod in prods:
                o = Product()
                o.from_dict(prod)
                print(o.__dict__)
                
                xstore.save(o)
                
        xstore.flush()
    except Exception as e:
                print("insert failed")
                print(e)
                

def _load_dup_product(df,xstore):
    dup_df = df[df['name'].duplicated()==True]
    prods = dup_df.to_dict(orient='record')
    try:
        for prod in prods:
            o = Product()
            o.from_dict(prod)
            print(o.__dict__)
            xstore.update(o,update_by=['name'])
        xstore.flush()
    except Exception as e:
        print("already existed, skipping update")
        print(e)



def load_product(df,xstore):
    
    df = df[['gid','name','variant']]
    df = df.fillna('')

    _load_undup_product(df,xstore)
    _load_dup_product(df,xstore)

def _load_category_node(df,xstore):
    print("loading category node")
    df = df[['cat_id','cat_item']]
    df = df.rename(columns={'cat_id':'gid','cat_item':'name'})
    print(df.head())
    categories = df.to_dict(orient='record')
    for c in categories:
        o = Category()
        o.from_dict(c)
        print(o.__dict__)
        try:
           xstore.save(o)
        except Exception as e:
           print(e)
    xstore.flush()
        

def _load_category_tree(df,xstore):
    print("loading category tree")
    df = df.rename(columns={'cat_id':'current','cat_parent':'parent'})
    print(df.head())
    category_tree = df.to_dict(orient='record')
    for r in category_tree:
        t = CategoryTree().relatesObj(
                entity='category',identifier='gid',
                value=r['current'], plays='current').withObj(
                    entity='category',identifier='gid',
                    value=r['parent'], plays='parent')
        # print(t.__dict__)
        xstore.relates(t,filter=lambda l,r: l['value'] != 0 and r['value'] != 0 )
    xstore.flush()


def load_category(df,xstore):
    _load_category_node(df,xstore)


    

def build_category_tree(df,xstore):
    _load_category_tree(df,xstore)




def relate_category_product(df, xstore):
    rel_list = df.to_dict(orient='record')
    for r in rel_list:
        rel = CategorizedRel().relatesObj(entity='product',identifier='gid',
                value=r['product_gid'],plays='categorized-as').withObj(entity='category',
                        identifier='gid',value=r['category_gid'],plays='container-of')
        xstore.relates(rel)
    xstore.flush()


    
def relate_product_brand(df2, xstore):
    rel_list = df2.to_dict(orient='record')
    for r in rel_list:
        rel = ProducedRel().relatesObj(entity='product',identifier='gid',
                value=r['product_gid'],plays='produce').withObj(entity='brand',
                        identifier='gid',value=r['brand_gid'],plays='produced-by')
        xstore.relates(rel)
    xstore.flush()


