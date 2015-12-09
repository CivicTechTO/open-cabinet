from db import get_db


def spot_missing(YEAR_START, YEAR_END):
    missing_list = list()

    with get_db() as cur:

        for year in range( YEAR_START, YEAR_END ):

            year_regex =  str(year)+'%'
            cur.execute("""SELECT
                            distinct id
                            FROM orders
                            WHERE 
                            CAST(id as VARCHAR) LIKE \'%s\'
                            ORDER by id ASC
                            ;""" % year_regex   )

            ids = cur.fetchall()
            ids = [ int(elem[0]) for elem in ids ]

            if len(ids) != 0:
                years_first = int(str(ids[0])[0:4]+"0001")
                expected = range( years_first, ids[-1]+1)

                curr_missing = [ elem for elem in expected if elem not in ids ] 
                missing_list.extend( curr_missing )


        for order_id in missing_list:
            cur.execute("""INSERT INTO missing(order_id) SELECT %s 
                            WHERE not exists 
                        ( SELECT 1 from missing WHERE order_id = %s);""", (order_id, order_id,) )
            cur.connection.commit()

    return missing_list

if __name__ == "__main__":
    spot_missing(1990, 2016)