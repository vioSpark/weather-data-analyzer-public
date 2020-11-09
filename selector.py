# coding: utf-8

# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates
# import matplotlib.ticker as mticker
# from mpl_finance import candlestick_ohlc
# import numpy as np
# from matplotlib import style
#
#
# class SelectorKernel:
#     def __init__(self, categories):
#         self.categories = categories
#
#
# def bytespdate2num(fmt, encoding='utf-8'):
#     strconverter = mdates.strpdate2num(fmt)
#
#     def bytesconverter(b):
#         s = b.decode(encoding)
#         return strconverter(s)
#
#     return bytesconverter
#
#
# style.use('tableau-colorblind10')
# print(plt.style.available)
#
# print(plt.__file__)
#
# """
# # two lines:
# x = [1, 2, 3]
# y = [5, 6, 4]
# x2 = [1, 2, 3]
# y2 = [10, 14, 12]
#
# plt.plot(x, y, label='first data')
# plt.plot(x2, y2, label='2nd data')
# """
# """
# bar
# charts:
# x = [2, 4, 6, 8, 10]
# y = [1, 2, 3, 6, 7]
#
# x2 = [1, 3, 5, 7, 9]
# y2 = [2, 3, 4, 1, 6]
# plt.bar(x, y, label='bars', color='r')  # color names or color name's first letter, or #FFFFFF notation
# plt.bar(x2, y2, label='bars2')
# """
# """
# # histograms:
# population_ages = [22, 55, 76, 102, 56, 87, 1, 5, 130, 113, 84, 34, 64, 65, 88, 97, 92, 3, 6, 12, 54, 24, 86, 100, 18,
#                    108, 109]
# # ids = [x for x in range(len(population_ages))]
#
# bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130]
# plt.hist(population_ages, bins, histtype='bar', rwidth=0.8, label='population')
# """
# """
# # scatter:
# x = [1, 2, 3, 4, 5, 6, 7, 8]
# y = [6, 4, 7, 8, 2, 7, 8, 1]
# plt.scatter(x, y, label='hears soviet anthem in the distance', color='r', marker='*', s=1000)
# """
# """
# stack
# plot:
# https: // www.youtube.com / watch?v = Z81JW1NTsO8 & list = PLQVvvaa0QuDfefDfXb9Yf0la1fPDKluPF & index = 5
# pie
# charts
# are
# existing as well
# """
# fig = plt.figure()
# ax1 = plt.subplot2grid((1, 1), (0, 0))
# date, openp, highp, lowp, closep, adj_closep, volume = np.loadtxt('temp.csv', delimiter=',', unpack=True,
#                                                                   converters={0: bytespdate2num('%Y-%m-%d')},
#                                                                   max_rows=100)
# """
# Very
# ugly
# stock
# price
# stuff(
# for demonstrating customization):
#     ax1.plot_date(date, closep, '-', label='Price')
# ax1.fill_between(date, closep, closep[0], where=(closep > closep[0]), alpha=0.3, facecolor='g', label='gain')
# ax1.fill_between(date, closep, closep[0], where=(closep < closep[0]), alpha=0.3, facecolor='r', label='loss')
# ax1.axhline(closep[0], color='k', linewidth=5)
#
# for label in ax1.xaxis.get_ticklabels():
#     label.set_rotation(45)
# ax1.grid(True)
# # ax1.xaxis.label.set_color('m')
# # ax1.yaxis.label.set_color('r')
# ax1.set_yticks([0, 100, 200, 300, 400, 500, 600, 700])
#
# ax1.spines['left'].set_color('c')
# ax1.spines['right'].set_visible(False)
# ax1.spines['top'].set_visible(False)
# ax1.spines['left'].set_linewidth(5)
# ax1.tick_params(axis='x', colors='#F06215')
# """
# """
# cadles(ohlc):
# x = 0
# y = len(date)
# ohlc = []
# while x < y:
#     append_me = date[x], openp[x], highp[x], lowp[x], closep[x], volume[x]
#     ohlc.append(append_me)
#     x += 1
#
# candlestick_ohlc(ax1, ohlc, width=0.4, colorup='g', colordown='r')
#
# # this fails
# for label in ax1.xaxes.get_ticklabels():
#     label.set_rotation(45)
# """
# ax1.plot(date, closep)
# ax1.plot(date, openp)
#
# plt.xlabel('Date')
# plt.ylabel('Price')
# plt.title('Sample text\nasdasd')
# plt.legend()
# plt.subplots_adjust(left=0.09, bottom=0.2, right=0.94, top=0.90, wspace=0.2, hspace=0)
#
# plt.show()
"""
animate and annotations
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

style.use('fivethirtyeight')
fig = plt.figure()
ax1 = fig.add_subplot(1, 1, 1)

xl = 1
yl = 1


def animate(i):
    graph_data = open('example', 'r').read()
    lines = graph_data.split('\n')
    xs = []
    ys = []
    for line in lines:
        if len(line) > 1:
            x, y = line.split(',')
            xs.append(float(x))
            ys.append(float(y))
    ax1.clear()
    ax1.plot(xs, ys, label='sample data')
    font_dict = {'family': 'serif',
                 'color': 'darkred',
                 'size': 15}
    ax1.text(xs[1], ys[1], 'more sample text', fontdict=font_dict)
    bbox_props= dict(boxstyle='round', fc='w', ec='k', lw=1)
    ax1.annotate('Bad News!', (xs[11], ys[11]), xytext=(0.8, 0.9), textcoords='axes fraction',
                 arrowprops=dict(facecolor='grey', color='grey'), bbox=bbox_props)


# ani = animation.FuncAnimation(fig, animate, interval=100, fargs=(xl, yl))
ani = animation.FuncAnimation(fig, animate, interval=10000)
plt.show()
"""
# from mpl_toolkits.mplot3d import axes3d
# import matplotlib.pyplot as plt
# import numpy as np
#
# fig = plt.figure()
# ax1 = fig.add_subplot(111, projection='3d')
# """
# # 3d part 1:
# x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# y = [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]
# z = [9, 2, 7, 9, 2, 0, 3, 5, 8, 2]
#
# ax1.plot(x, y, z)
#
# x2 = [-1, -2, -3, -4, -5, -6, -7, -8, -9, -10]
# y2 = [-1, -4, -9, -16, -25, -36, -49, -64, -81, -100]
# z2 = [9, 2, 7, 9, 2, 0, 3, 5, 8, 2]
#
# ax1.scatter(x, y, z, marker='x', c='r')
# ax1.scatter(x2, y2, z2, marker='o', c='orange')
#
# x3 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# y3 = [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]
# z3 = np.zeros(10)
#
# dx = np.ones(10)
# dy = np.ones(10) * 10
# dz = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
#
# ax1.bar3d(x3, y3, z3, dx, dy, dz)
# """
# """
# # 3d part 2:
#
# x, y, z = axes3d.get_test_data()
#
# print(axes3d.__file__)
# ax1.plot_wireframe(x, y, z, rstride=5, cstride=5)
#
# ax1.set_xlabel('x axis')
# ax1.set_ylabel('y axis')
# ax1.set_zlabel('z axis')
#
# plt.show()
# """
