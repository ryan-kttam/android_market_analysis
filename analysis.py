import pandas as pd
from collections import Counter
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

## Learn more about the android market

# reading the data
data = pd.read_csv('C:/Github/android_market_analysis/googleplaystore.csv')
# check the first two rows of the data and make sure we imported correctly
data.head(5)
len(data)
list(data)

# check how many rows in the data
print (len(data))
# check if there is any missing or null values
data.isnull().sum() # out of 10841 rows, there are 1474 missing ratings.
sum(data.Size == 'Varies with device') # there are 1695 rows does not have a size due to the app size varies with device.

# Data Preprocessing
# check whether the size are using the same unit.
size_unit = [unit[-1] for unit in data.Size]
Counter(size_unit) # there are 1 app ending with '+', 8829 apps ending with MB and 316 apps ending with kb. (1695 apps varies with device)
# Something seems odd with the app size unit as '+', I decided to take a look:
data.loc[[i=='+' for i in size_unit] ,]
# This app is definitely weird. Not only does it have invalid size unit, but it's rating also doesn't make sense at all.
# Due to it's rating, size, content Rating and Anderoid Ver does not provide any information, it is safe to remove this record from the data.
data = data.loc[[i!='+' for i in size_unit] ,]
# Standardize all app size to MB, remove all size unit tags and change to numeric
size_unit = [unit[-1] for unit in data.Size]
kb_loc = [i=='k' for i in size_unit] # find all indexes of KB
mb_loc = [i=='M' for i in size_unit] # find all indexes of MB
data.loc[kb_loc ,'Size'] = [pd.to_numeric(kb[:-1])/1024.0 for kb in data.loc[kb_loc, 'Size']]
data.loc[mb_loc ,'Size'] = pd.to_numeric([mb[:-1] for mb in data.loc[mb_loc ,'Size']])
# (next: remove installs less than 49
def fotmat_install(d):
    return d.replace(',','').replace('+','')
data.Installs = pd.to_numeric([fotmat_install(i) for i in data.Installs])
data['Reviews'] = pd.to_numeric(data['Reviews'])

# this function is to filter out rows that do not have size or ratings.
def is_number(i):
    try:
        float(i)
        return ~np.isnan(i)
    except:
        return False

def get_mode(dict):
    occurrence = 0
    key = 0
    for mb, count in dict.items():
        if count >= occurrence:
            occurrence = count
            key = mb
    return key

size_data = data.loc[ [is_number(c) for c in data.Size], ]
size_list = list(size_data.Size)
#plot1 = sns.distplot(size_list, hist=False)
plot1 = sns.kdeplot(size_list, shade=True)
plot1.set_title('Distribution of App Size', size=15)
plot1.set_xlabel('Size (MB)')
plot1.set_ylabel('Density')
plot1.set_xlim(0,100)
plot1.set_ylim(0,)
plot1_mean = np.mean(size_list)
# plot1.text(x=plot1_mean+1,y=0.052, s='Mean: '+str(np.round(plot1_mean,1))+' MB')
plot1_median = np.median(size_list)
# plot1.text(x=plot1_median+1,y=0.055, s='Median: '+str(np.round(plot1_median,1))+' MB')
mode = Counter([round(i,0) for i in size_list])
p1_mode = get_mode(mode)
line1, = plot1.plot([plot1_mean, plot1_mean], [0, .0145], lw=1)
line2, = plot1.plot([plot1_median, plot1_median], [0, .0225], lw=1)
line3, = plot1.plot([p1_mode, p1_mode], [0, .041], lw=1)
#plot1.text(x=plot1_mode+1,y=0.058, s='Mode: '+str(plot1_mode)+' MB')
plot1.legend((line3, line2, line1),
('Mode: '+str(p1_mode),
'Median: '+str(np.round(plot1_median, 0)),
'Mean: ' + str(np.round(plot1_mean, 0))))
# comment: The average app file size for android is 22 MB. However, this is due to a small number of apps with large file size.
# Majority of the app size are clustered in 0 - 10 MB, with 4MB being the most common.

rating_data = data.loc[ [is_number(c) for c in data.Rating], ]
rating_list = rating_data.Rating
plot2 = sns.kdeplot(rating_list, shade=True)
# plot2 = sns.distplot(rating_list, hist=False, shade=True)
plot2.set_title('Distribution of Average User Rating',size=15)
plot2.set_xlabel('User Rating')
plot2.set_ylabel('Density')
plot2.set_xlim(1,5)
plot2.set_ylim(0,)
p2_mean = np.mean(rating_list)
p2_median = np.median(rating_list)
p2_mode = get_mode(Counter(round(rating_list,1)))
line1, = plot2.plot([p2_mean, p2_mean], [0, 0.97], lw=1)
line2, = plot2.plot([p2_median, p2_median], [0, 1.12], lw=1)
line3, = plot2.plot([p2_mode, p2_mode], [0, 1.16], lw=1)
#plot1.text(x=plot1_mode+1,y=0.058, s='Mode: '+str(plot1_mode)+' MB')
plot2.legend((line1, line2, line3),
('Mean: '+str(np.round(p2_mean, 1)),
'Median: '+str(np.round(p2_median, 1)),
'Mode: ' + str(p2_mode))
)

round(sum(rating_list > 3.0)/ len(rating_list) * 100.0, 2)
# Comment: among all valid ratings, less than 4% rated below or equal 3.0.
# Majority of the ratings are between 4.0 and 5.0, meaning people generally give high ratings to apps.
len(size_data.groupby(by=['Category']))
size_data['Size'] = pd.to_numeric(size_data['Size'])
size_data_by_category = size_data.groupby(by=['Category'])['Size'].median().sort_values(ascending=False)
keep = list(size_data_by_category[:5].index) + list(size_data_by_category[-5:].index)
idx_to_keep = [i in keep for i in size_data['Category']]
size_data_top5_bottom5 = size_data.loc[idx_to_keep, ]

def get_top5_bottom5(data, by_category):
    group = []
    for i in data.Category:
        if i in list(by_category[:5].index):
            group.append('Top 5 in Size')
        else:
            group.append('Bottom 5 in Size')
    return group

group = get_top5_bottom5(size_data_top5_bottom5,size_data_by_category)
size_data_top5_bottom5['Rank'] = group
size_order = size_data_top5_bottom5.groupby(by=['Category'])['Size'].median().sort_values(ascending=False).index
plot3 = sns.boxplot(y='Category', x='Size', hue='Rank', data=size_data_top5_bottom5, order=size_order)
plot3.set_yticklabels(plot3.get_yticklabels(), fontsize=8, ha='right', rotation=20)
plot3.set_xlim(0,100)
plot3.set_title('App Size by Category', size=15)
plot3.set_xlabel('Size (MB)')
plot3.set_ylabel('Category')
plot3.legend(loc='lower right')

# Here I only include the top 5 and the bottom 5 categories in app file size. As we can see in the boxplot,
# games generally has larger file size(median around 40), while libraries and demo has the smallest size (median less than 4).

rating_by_category = rating_data.groupby(by=['Category'])['Rating'].median().sort_values(ascending=False)
keep = list(rating_by_category[:5].index) + list(rating_by_category[-5:].index)
idx_to_keep = [i in keep for i in rating_data['Category']]
rating_data_top5_bottom5 = rating_data.loc[idx_to_keep, ]

rating_data_top5_bottom5['Rank'] = get_top5_bottom5(rating_data_top5_bottom5, rating_by_category)
rating_order = rating_data_top5_bottom5.groupby(by=['Category'])['Rating'].median().sort_values(ascending=False).index
plot4 = sns.boxplot(y = 'Category', x = 'Rating', hue='Rank', data=rating_data_top5_bottom5, order=rating_order)
plot4.set_yticklabels(plot4.get_yticklabels(),rotation=20, fontsize=8, ha='right')
plot4.set_title('App Rating by Category',size=15)
plot4.set_xlabel('Rating')
plot4.set_ylabel('Category')
plot4.set_xlim(1, 5)

# Rating do not seem to differ much in categories, but we definitely see a difference when we compare the top rating
# app category (Health & Fitness) and the worst rating category (Dating), with the median difference of 0.4



type_count = data.Type.value_counts()
free, paid = rating_data.groupby(by=['Type'])['Rating'].mean()
plt.pie(type_count, labels=type_count.index, autopct='%.2f%%', colors=['paleturquoise','salmon'], shadow=True, startangle=90)
plt.title('Free vs Paid App distribution', size=15)
plt.text(x=.8,y=-.8,s='Average Rating:')
plt.text(x=.8,y=-.9,s='Free: '+str(np.round(free, 2)))
plt.text(x=.8,y=-1,s='Paid: '+str(np.round(paid, 2)))

# Almost 93% of the apps in the android market are free, and the average rating between the two are similar.

category_count = data.Category.value_counts().sort_values(ascending=False)
plot5 = sns.barplot(y=category_count.index,x=category_count, orient='h')
plot5.set_yticklabels(plot5.get_yticklabels(),rotation=20, fontsize=8, ha='right')
plot5.set_title('Number of Apps by Category',size=15)
plot5.set_xlabel('Number of Apps')
plot5.set_ylabel('Category')

install_by_category = data.groupby(by='Category')['Installs'].sum().sort_values(ascending=False)
install_by_category = install_by_category/1000000000 # in billion
plot7 = sns.barplot(y=install_by_category.index,x=install_by_category, orient='h')
plot7.set_yticklabels(plot7.get_yticklabels(),rotation=20, fontsize=8, ha='right')
plot7.set_title('Number of Installs by Category', size=15)
plot7.set_xlabel('Installs (in Billion)')
plot7.set_ylabel('Category')

# it is interesting that 'Family' is only rank 6th in the number of installs while it actually has almost doubled the
# number of apps of 'Game'. It shows that app developers or companies maybe on the wrong focus since android users seem
# to think other categories such as 'Communication' and 'Productivity' apps are more important than 'Family' apps.

# Suppose a game design company is developing a game that targets to attract millions players on Android, they are open-minded
# and are willing to accept any genre as long as the game will be popular. What game genre should they develop?

# Let's get an idea about what other game design companies think of game genres:
gaming_app = data.loc[data.Category == 'GAME',]
gaming_app.Genres = [i.split(';')[0] for i in gaming_app.Genres] # use loc?
game_type = gaming_app.Genres.value_counts()*100/ len(gaming_app)

plot8 = sns.barplot(y=game_type.index, x=game_type, orient='h')
plot8.set_title('Game Genres Distribution by App Count', size=15)
plot8.set_ylabel('Game Genres')
plot8.set_xlabel('Percentages')
plot8.text(y=0+0.2, x=game_type[0], s=str(round(game_type[0],1))+'%')
plot8.text(y=len(game_type)-1+0.2, x=game_type[len(game_type)-1], s=str(round(game_type[len(game_type)-1],1))+'%')

# Wow, 'Action' game almost hold one third of the gaming apps, with over 32%, while simulation only hold about 1% of the market.
# If 'Action' games are so popular, then 'Action' Games must be the way to go! But wait, this is only parts of the story. We need to
# consider what customers think about the market too. We can accomplish this by understanding the number of installs by different genres.

install_by_game_genres = gaming_app.groupby(by='Genres')['Installs'].sum().sort_values(ascending=False)
install_by_game_genres = install_by_game_genres/1000000000 # in billion
install_by_game_genres_pct = install_by_game_genres/sum(install_by_game_genres )


plot9 = sns.barplot(y=install_by_game_genres.index,x=install_by_game_genres, orient='h')
plot9.set_yticklabels(plot9.get_yticklabels(), rotation=20, fontsize=8, ha='right')
plot9.set_title('Number of Installs by Game Genre', size=15)
plot9.set_xlabel('Installs (in Billion)')
plot9.set_ylabel('Genre')
plot9.text(y=0+0.2, x=install_by_game_genres[0]-2, s=str(round(install_by_game_genres[0],1))+', '+ str(round(install_by_game_genres_pct[0]*100.0))+'%')
plot9.text(y=len(install_by_game_genres)-1+0.2, x=install_by_game_genres[len(install_by_game_genres)-1],
s=str(round(install_by_game_genres[len(install_by_game_genres)-1],1))+', '+ str(round(install_by_game_genres_pct[len(install_by_game_genres)-1]*100.0))+'%')

# It turns out that 'Action' games are not the most popular game in Android market, according to the number of installs by game genre, which ranks 2nd,
# while 'Arcade' holds the top spot.
# Even though Arcade games are popular among all game genres, I would not develop an Arcade game if i were the game design company.
# 20% of the market share in games are Arcade. It means that there is an Arcade game for every five games. It is difficult to stand out from the crowd
# when you have many other competitors in the same genre. 'Casual' games, on the other hand, shows a great potential as it held about 20% of the market shares in installs,
# while less than 5% of the game are 'Casual' in the market right now. # It means that people likes to play causal games and currently they are not as saturated as
# Action games and Arcade games.

# What ratings should I be aiming for if I am developing games?

rating_by_game_genres = gaming_app.groupby(by=['Genres'])['Rating'].median().sort_values(ascending=False).index
plot10 = sns.boxplot(y = 'Genres', x = 'Rating', data=gaming_app, order=rating_by_game_genres)
plot10.set_yticklabels(plot10.get_yticklabels(),rotation=20, fontsize=8, ha='right')
plot10.set_title('Game Rating by Genre',size=15)
plot10.set_xlabel('Rating')
plot10.set_ylabel('Genres')
plot10.set_xlim(3.25,)

# According to this boxplot, most of the game genre has a median of 4.25. Depending on which genre the company choose,
# a more concise boxplot is available for each genre. For example for 'Casual' Games, we should be expecting a rating of 4.4 (lower quartile)
# and aiming for 4.5 (upper quartile) if the company want the game to succeed. 'Casual' Game also has a smaller variance comparing other game genres like
# 'Racing' and 'Board' games, which benefits us as we understand that players in 'Casual' game generally is pretty satisfied with the game.

# Reviews

# Reivews are important for software companies, as they are one of the most straight forward way to listen from the users.
# In fact, people do not leave comments or reviews for nothing. they write reviews because they have something to praise or complain about the app.
# That is why reviews are so important for any companies. As a result, Companies should definitely pay attention to those reviews.
# Lets begin with checking the number of reviews by category

reviews_by_category = data.groupby(by='Category')['Reviews'].sum().sort_values(ascending=False)
reviews_by_category = reviews_by_category/1000000.0 # in million

plot11 = sns.barplot(y=reviews_by_category.index,x=reviews_by_category, orient='h')
plot11.set_yticklabels(plot11.get_yticklabels(),rotation=20, fontsize=7.5, ha='right')
plot11.set_title('Number of Reviews by Category',size=15)
plot11.set_xlabel('Reviews (in Million)')
plot11.set_ylabel('Category')
plot11.text(y=0+0.35, x=reviews_by_category[0], s=str(round(reviews_by_category[0],1)), size=8)
plot11.text(y=len(reviews_by_category)-1+0.2, x=reviews_by_category[len(reviews_by_category)-1],
s=str(round(reviews_by_category[len(reviews_by_category)-1],1)), size=8)

# This graph is not very informative as 'Game' takes over the reviews. It is actually expected given the fact that 'games' has
# a much larger numbers in installs compared to less popular category like 'Beauty' and 'Events'
# The story would be clearer if we divide them by the number of installs according to their category. This way we are able to understand
# how likely a user writes a review in a given category.

data_by_category = data.groupby(by='Category')
likelihood_to_review = (data_by_category.Reviews.sum()/data.groupby(by='Category')['Installs'].sum().sort_index()).sort_values(ascending=False)*100

plot11 = sns.barplot(x=likelihood_to_review, y=likelihood_to_review.index)
plot11.set_yticklabels(plot11.get_yticklabels(), rotation=20, fontsize=8, ha='right')
plot11.set_title('Likelihood to Write Reviews', size=15)
plot11.set_xlabel('Percentage')
plot11.set_ylabel('Category')
plot11.text(y=0+0.4, x=likelihood_to_review[0], s=str(round(likelihood_to_review[0],1))+'%', size = 9)
plot11.text(y=len(likelihood_to_review)-1+0.4, x=likelihood_to_review[len(likelihood_to_review)-1],
s=str(round(likelihood_to_review[len(likelihood_to_review)-1],1))+'%', size = 9)

# This plot shows a surprising result. 'Comics' actually holds the top spot with 6%, meaning people who downloaded 'Comics'
# tends to write more reviews compared to other app categories. Categories that has the least likelihold to have reviews
# are 'News & Magazines', 'Productivity', 'Travel & Local', and 'Events'. They all have less than 1% of the users to write reviews.
# They will probably need to find another way to get feedback regarding the performance of the apps.

# In this post, I explored :
# - How to prepare data for data visualization
# - What does Android Market look like now
# - How does category affect the average size of an app.
# - How would a game design company use Android Market data to analyze current gaming market.
# - How satisfy users feel for different app categories.
# - What categories should and shouldn't pay extra attention to reviews.