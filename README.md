my english is very very very bad . luckily , ai is so easy that i can read english sentense easily. 
i will use chinese . hahahaha.

2026/2/21   2 ；00
这是一个非常简单的AI Agent项目，我甚至是刚学习了一点点相关知识就迫不及待想要做点什么出来了。

小宅demo（这个项目的名字）的功能很简单，输入一段文字，小宅会帮你打开对应exe格式的文件。如：“小宅小宅，帮我打开原神”，然后原神就启动了。

首先是json_save.py文件，它的作用是生成包含多个以程序名称、程序位置和口令为单元的的json文件；
其次是skills.py文件，它的作用是获取LLM大模型回复的口令，然后匹配对应json中对应的口令，根据json中的程序地址打开exe程序；
最后是main.py主程序，它的作用是通过api接口调用大模型，根据预设的prompt返回口令，然后调用skills中函数打开程序。

整个过程相当简单，但我现在超级困，上传完初版demo我就睡觉了，明天再慢慢优化。嗷呜~ ~ ~
