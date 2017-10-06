# GitHub 软件项目推荐系统
## 安装
### 爬虫的依赖包
```bash
pip install scrapy nltk
```
nltk 中需要安装stopwords词库
```bash
python
import nltk
nltk.download('stopwords')
```

## 爬虫
### 启动爬虫
通过`python crawl_github/main.py`启动爬虫。

### 爬取结果
爬虫的结果以csv 文件保存在`crawl_github/csv`目录下:
* Repo.csv 文件: 保存repository的基本信息，
文件格式如下：
```csv
url,description,language,name
https://github.com/eastridge/eastridge.me,Ryan's Website,JavaScript|HTML,eastridge.me
```
* RepoReadme.csv 文件: 保存repository的README单词(已过滤基本停用词)，
文件格式如下(0表示该项目没有README文件)：
```csv
readme,name
0,eastridge.me
```
* RepoSource.csv 文件: 保存repository的源代码单词(已过滤代码的停用词)，
文件格式如下(0表示该项目没有源代码)：
```csv
source,name
0,eastridge.me
```
* UserItem.csv 文件: 用户与项目之间的行为，
格式如下(10表示用户创建此项目，6表示用户fork此项目，3表示用户watch此项目，1表示用户star此项目):
```csv
action,user_name,repo_name
10,eastridge,eastridge/eastridge.me
6,eastridge,jeromegn/Backbone.localStorage
1,stefanerickson,nylas/nylas-mail
```
### 迭代深度（爬取规模）
因为要保证数据完整性，不能在settings里设置爬取深度。
应修改`crawl_github/spiders/github_spider_ol.py`文件，约27行：

```python
DEPTH = 3 # 控制迭代深度，3指函数递归深度为3次，即 用户A->用户1,2,3->用户i,ii,iii
```
### 删除中间文件
爬虫运行过程需要下载项目文件，这些文件保存在`crawl_github/zip`文件夹下。
爬虫在爬取时，若该文件夹下有项目的zip文件，则不再重新下载。
使用者可以通过删除其中的zip文件，以释放磁盘空间。

### 添加爬取watch行为
因为增加watch行为后推荐效果不好，程序没有爬取watch行为。
如有需要，用户可以修改`crawl_github/spiders/github_spider_ol.py`文件，约80行处：
```python
watch_url = base_url + '/' + repo_url + '/watchers'
# yield Request(watch_url, meta={"step": step}, callback=self.parse_watch)　＃打开该行注释
```
改成
```python
watch_url = base_url + '/' + repo_url + '/watchers'
yield Request(watch_url, meta={"step": step}, callback=self.parse_watch)　＃打开该行注释
```
## 推荐程序
推荐程序的具体原理可以参考论文“Scalable Relevant Project Recommendation on GitHub”,
`engine.py`为程序的单机版，`engine2ver.py`是在Apache Spark框架上运行的并行化版本
### 运行
运行`python engine.py`即可运行程序的单机版，

运行`python engine2ver.py`即可运行程序的Apache Spark版。

程序读取项目文件（hrepo.csv）和用户-项目行为（ga_with_repo.csv）文件为输入，并产生推荐结果保存在csv文件中。
输入输出文件的格式请参考`data/hrepo.csv`、`data/ga_with_repo.csv`和`rec.csv/result.csv`。

## 工具
* `make_dataset.py`可以将爬虫产生的结果生成推荐程序所需要的`data/hrepo.csv`和`data/ga_with_repo.csv`文件。
* `div.py`可以将测试文件随机划分为训练集和测试集。
* `evaluation.py`用来计算推荐结果的Accuracy，Recall，Precision，Popularity，mAP和mRR。
* `eval_feedback.py`用来模拟用户生成反馈。
