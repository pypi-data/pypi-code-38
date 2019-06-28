def filter_product_category_relation(df):
    '''
        should pass df
    '''
    prodcat_df = df[['prod_id','cat_id']]
    prodcat_df = prodcat_df.rename(columns={'prod_id':'product_gid','cat_id':'category_gid'})
    prodcat_df = prodcat_df.drop_duplicates()
    return prodcat_df

def filter_product_brand_relation(df):
    prodbrand_df = df[['prod_id','brands_id']]
    prodbrand_df = prodbrand_df.rename(columns={'prod_id':'product_gid','brands_id':'brand_gid'})
    return prodbrand_df

def filter_category_tree_relation(df):
    categtree_df = df[['cat_id','cat_parent']]
    categtree_df = categtree_df.drop_duplicates()
    return categtree_df

def filter_category_entity(df):
    cat_df = df[['cat_id','cat_parent','cat_item','cat_status','cat_has_shade']]
    cat_df = cat_df.drop_duplicates()
    return cat_df

def filter_brand_entity(df):
    brand_df = df[['brands_id','brands_item','brands_slug','brands_desc']]
    brand_df = brand_df.rename(columns={'brands_id':'gid','brands_item':'name','brands_slug':'slug','brands_desc':'desc'})
    brand_df = brand_df[['gid','name','slug']]
    brand_df = brand_df.drop_duplicates()
    return brand_df

def filter_product_entity(df):
    product_df = df
    product_df = product_df[product_df['review_deletestatus'] != 'y']
    product_df = product_df.fillna('').sort_values(by=['prod_item']).drop_duplicates()
    product_df = product_df.rename(columns={'prod_id':'gid','brands_id':'brand_gid','prod_item':'name','prod_slug':'slug','prod_type':'variant'})
    product_df = product_df[['gid','brand_gid','name','slug','variant']]
    return product_df