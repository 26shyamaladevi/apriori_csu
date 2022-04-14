from flask import Flask, render_template, request ,redirect, url_for
from itertools import combinations

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route('/', methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        uploaded_file.save(uploaded_file.filename)
    
    file_name = uploaded_file.filename
    min_support = int(request.form['min_Support'])
    f = open(file_name,"r")
    data = f.read()
    find_lines = data.split("\n")
    rows = len(find_lines) - 1
    min_sup = min_support/rows
    total_sets = []

    for find_line in find_lines:
        if (find_line.strip() != ""):  
            temp_list = []
            split_values = find_line.split(", ")
            for split_value in split_values[1::]:  
                try:  
                    temp_list.append(int(split_value.strip()))
                except:
                    temp_list.append(int(split_value))
            total_sets.append(temp_list)

    total_result_set = apriori_gen(total_sets,min_support=min_sup)
    print("Final result set : ",total_result_set)    
    return render_template('result.html',file_name=file_name,min_support=min_support,total_result_set=total_result_set)

def find_frequent_1_itemsets(var_sets):  
    candidate_set_1 = []
    for transactions_set in var_sets:
        for transaction_set in transactions_set:
            transaction_set = frozenset([transaction_set])
            if transaction_set not in candidate_set_1:
                candidate_set_1.append(transaction_set)
    return candidate_set_1



def apriori_gen(var_sets, min_support):
    final_result_set = []  
    candidate_set_1 = find_frequent_1_itemsets(var_sets)       
    frequent_item, item_support_dict, res = create_frequent_item(var_sets, candidate_set_1, min_support)
    frequent_items = [frequent_item]
    final_result_set.append(res)
    k = 0
    while len(frequent_items[k]) > 0:
        frequent_item = frequent_items[k]
        c_k = create_candidate_k(frequent_item, k)
        frequent_item, item_support, res = create_frequent_item(var_sets, c_k, min_support)
        final_result_set.append(res)
        frequent_items.append(frequent_item)
        item_support_dict.update(item_support)
        k += 1
    if not final_result_set: return final_result_set
    final_result_set.pop()  
    total_result_set = remove_subsets(final_result_set)  
    return total_result_set

def create_frequent_item(var_sets, c_k,min_support):  
    count_sets = {}
    res = []
    Condition=False;
    count_sets= has_infrequent_subset(c_k,var_sets)
    number_of_rows = len(var_sets)
    frequent_sets = []
    item_support = {}

    for item in count_sets:
        support = count_sets[item] / number_of_rows
        if support >= min_support:
            frequent_sets.append(item)
            res.append(list(item))

        item_support[item] = support
    return frequent_sets, item_support, res

def has_infrequent_subset(c_k,var_sets):
    count_items = {}
    for i in var_sets:
        for t in c_k:
            if t.issubset(i):
                if t not in count_items:
                    count_items[t] = 1
                else:
                    count_items[t]+=1
    return count_items

def create_candidate_k(frequent_item,k_value):  
    c_k = []
    if k_value == 0:  
        for f1, f2 in combinations(frequent_item, 2):
            item = f1 | f2  
            c_k.append(item)
    else:
        for f1, f2 in combinations(frequent_item, 2):
            intersection = f1 & f2
            if len(intersection) == k_value:
                item = f1 | f2
                if item not in c_k:
                    c_k.append(item)
    return c_k

def remove_subsets(v): 
    no_of_items = 0
    final_result_list = []
    if(len(v)!=0):
        
        for k in range(len(v) - 1):
            out_sub_list = []
            for item in v[k]:
                exist = 0
                for rep in range(k + 1, len(v)):
                    for co in v[rep]:
                        if set(item).issubset(set(co)):
                            exist = 1
                if (exist == 0):
                    out_sub_list.append(item)
                    no_of_items += 1
            final_result_list.append(out_sub_list)
        final_result_list.append(v[len(v) - 1])  
        no_of_items += len(v[len(v) - 1])  
    no_of_items_str = "\n\nEnd - Total number of items: " + str(no_of_items)
    total_result_set = export_result(final_result_list)
    total_result_set += no_of_items_str
    return total_result_set

def export_result(result_array):
    total_result_set = ""
    total_result_set += "{ "
    for frequent_item in result_array:
        for item in frequent_item:
            total_result_set += "{ "
            f = ""
            new_item_list = []  
            for i in range(len(list(item))):
                new_item_list.append(list(item)[i])
            new_item_list.sort()
            for i in range(len(new_item_list)):
                f += str(new_item_list[i])
                if (i != len(new_item_list) - 1):
                    f += " , "
            total_result_set += f
            total_result_set += " }"
    total_result_set += " }"
    return total_result_set

if __name__ == "__main__":
    app.run()
