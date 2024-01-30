from Resources.resources import *
from Resources.IO import *
import os
import pandas as pd
import shutil


def get_returns(prob_h, prob_a, prob_d, h_odds, a_odds, d_odds):
    """
    :param prob_h: poisson probability of home win
    :param prob_a: poisson probability of away win
    :param prob_d: poisson probability of draw
    :param h_odds: bookie odds for home win
    :param a_odds: bookie odds for away win
    :param d_odds: bookie odds for draw
    :return: possible outcomes (monetary) for our poisson predictions
    """

    if (abs(prob_h - prob_a) <= 0.01) or (prob_d > prob_h and prob_d > prob_a):
        if d_odds > 0:
            return [prob_h, prob_a, prob_d, -100, -100, d_odds]
        else:
            return [prob_h, prob_a, prob_d, d_odds, d_odds, 100]
    if prob_h > prob_a and prob_h > prob_d:
        if h_odds > 0:
            return [prob_h, prob_a, prob_d, h_odds, -100, -100]
        else:
            return [prob_h, prob_a, prob_d, 100, h_odds, h_odds]
    if prob_a > prob_h and prob_a > prob_d:
        if a_odds > 0:
            return [prob_h, prob_a, prob_d, -100, a_odds, -100]
        else:
            return [prob_h, prob_a, prob_d, a_odds, 100, a_odds]


def split_historical_df(df, league_dir, hist_dfs_dir, x):
    """
    Function splits our historical dataframe into smaller dataframes by season
    :param hist_dfs_dir:
    :param df: historical dataframe
    :param league_dir: directory to the league we are working with
    """

    dfs = dict(tuple(df.groupby('Season')))
    keys_list = list(dfs)
    if not os.path.isdir(hist_dfs_dir):
        os.mkdir(hist_dfs_dir)
    f_name = hist_dfs_dir + 'hist_df_'
    for i in range(len(keys_list)):
        if i >= 3:
            file = f_name + keys_list[i] + '.csv'
            df = dfs[keys_list[i]]
            write_df(df, file)
    os.system('find . -name "*.DS_Store" -type f -delete')


def sort_poisson_directory(files):
    new_list = []
    nums = []
    for file in files:
        file_ = file[7:]
        file_ = file_[:-4]
        nums.append(int(file_.split('_')[1]))
        new_list.append([file_.split('_')[1], file])
    nums.sort()
    ordered_list = []
    for num in nums:
        for i in range(len(new_list)):
            if int(new_list[i][0]) == num:
                ordered_list.append(new_list[i][1])
    return ordered_list


def merge_large_dfs(hist_dfs_dir, hist_preds_dfs_dir, training_dir, x):
    """
    Function merges historical data from historical dataframes to prediction dataframes
    :param x:
    :param hist_dfs_dir: directory with historical dataframes
    :param hist_preds_dfs_dir: directory with prediction dataframes
    :param training_dir: directory with the newly assembled dataframes
    """

    hist_dfs_files = sorted(os.listdir(hist_dfs_dir))
    hist_preds_dfs_files = sort_poisson_directory(os.listdir(hist_preds_dfs_dir))

    for i in range(len(hist_dfs_files)):
        out_file = training_dir + str(i + 1) + '_training.csv'
        hist_df = read_df(hist_dfs_dir + hist_dfs_files[i])
        pred_df = read_df(hist_preds_dfs_dir + hist_preds_dfs_files[i])
        pred_df['Home Win odds'] = hist_df['Home Win odds'].tolist()
        pred_df['Away Win odds'] = hist_df['Away Win odds'].tolist()
        pred_df['Draw odds'] = hist_df['Draw odds'].tolist()
        pred_df['Season'] = hist_df['Season'].tolist()

        pred_df['FTR'] = hist_df['FTR'].tolist()
        for col in pred_df.columns:
            pred_df = pred_df[pred_df[col] != '-']
            pred_df = pred_df.dropna()

        write_df(pred_df, out_file)


def one_big_training(training_dir, out_file, x):
    """
    Function concatenates all dataframes from the training directory and writes it to a file containing
    new dataframe
    :param training_dir: training dataframes directory
    :param out_file: output file for dataframe
    """

    files = os.listdir(training_dir)
    n = len(files)
    for i in range(n - 1):
        for j in range(0, n - i - 1):

            sub_1 = files[j][0:2]
            if sub_1.isdecimal():
                sub_1 = int(sub_1)
            else:
                sub_1 = int(files[j][0:1])

            sub_2 = files[j + 1][0:2]
            if sub_2.isdecimal():
                sub_2 = int(sub_2)
            else:
                sub_2 = int(files[j + 1][0:1])

            if sub_1 > sub_2:
                files[j], files[j + 1] = files[j + 1], files[j]

    frames = []
    for file in files:
        frames.append(read_df(training_dir + file))
    df = pd.concat(frames)
    no_duplicates = df.drop_duplicates(keep=False)
    if x == 1:
        del no_duplicates['P(Home) ave']
        del no_duplicates['P(Away) ave']
        del no_duplicates['P(Draw) ave']
    write_df(no_duplicates, out_file)


def re_order_pred_dfs(hist_preds_dfs_dir):
    """
    Function adds game numbers column to poisson dataframes
    :param hist_preds_dfs_dir: poisson dataframes directory
    """

    pred_dfs = sorted(os.listdir(hist_preds_dfs_dir))
    for i in range(len(pred_dfs)):
        pred_df = read_df(hist_preds_dfs_dir + pred_dfs[i])
        game_num = pred_df['Unnamed: 0'].tolist()
        del pred_df['Unnamed: 0']
        pred_df['Game Number'] = game_num
        write_df(pred_df, hist_preds_dfs_dir + pred_dfs[i])


def post_poisson_train(league_dir, x):
    """
    Function incorporates functions from above to create on training dataframe
    :param x:
    :param league_dir: league directory
    """

    hist_file = league_dir + '/historical_df.csv'
    hist_dfs_dir = league_dir + 'hist_dfs/'
    hist_df = read_df(hist_file)
    split_historical_df(hist_df, league_dir, hist_dfs_dir, x=x)

    hist_preds_dfs_dir = league_dir + 'poisson/'
    # re_order_pred_dfs(hist_preds_dfs_dir)
    training_dir = league_dir + 'training_dfs/'
    final_training_file = league_dir + 'dataset.csv'
    if not os.path.isdir(training_dir):
        os.mkdir(training_dir)
    merge_large_dfs(hist_dfs_dir, hist_preds_dfs_dir, training_dir, x=x)
    one_big_training(training_dir, final_training_file, x)
    shutil.rmtree(hist_dfs_dir)
    shutil.rmtree(training_dir)


def main():
    league_dir = EPL
    post_poisson_train(league_dir, x=3)


if __name__ == '__main__':
    main()
