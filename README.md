## 工具介绍
Let’s Encrypt通配符证书申请，只能用DNS plugins的验证方式。其原理就是依照提示增加某个TXT记录的域名进行验证。整个流程都是需要配合certbot的提示并手动执行。  
如果想自动完成这个过程，根据官方文档提供的资料，需要写有两个hook脚本来替代人工操作：  
- **--manual-auth-hook**  
- **--manual-cleanup-hook**

强烈建议看完本人的这篇博文之后再来使用：《[LET’S ENCRYPT通配符证书的申请与自动更新（附阿里云域名的HOOK脚本）](http://blog.dreamlikes.cn/archives/1028)》

这个工具是专门针对阿里云（万网）域名使用的，其他域名供应商的请勿使用。

## 使用步骤
### 一、下载代码
```
git clone https://github.com/broly8/letsencrypt-aliyun-dns-manual-hook.git
```

### 二、配置appid和appsecret
首先去自己的阿里云域名管理后台，申请有增加和删除域名权限的appid和appsecret。具体申请步骤请自行摸索，网上应该有很多资料。  
然后把申请好的appid和appsecret填入到**config.ini**文件中。

### 三、申请通配符证书
官方的证书申请工具certbot，有两个参数 **--manual-auth-hook** 和 **--manual-cleanup-hook**  
即分别指定脚本，去增加TXT记录的域名和删除。

所以配合到本工具使用就是：
```
certbot certonly \
...
--manual-auth-hook 'python /path/to/manual-hook.py --auth' \
--manual-cleanup-hook 'python /path/to/manual-hook.py --cleanup'
```

如果你对certbot工具不熟悉，或者仅仅想申请自己的通配符域名，可以使用本人提供的另一个脚本工具 **letsencrypt-create.sh** ，使用方法很简单
```
sh letsencrypt-create.sh -m your-email@example.com -d yourdomain.com
```

如果想强制生成或者更新通配符证书，则使用 **-f** 参数
```
sh letsencrypt-create.sh -m your-email@example.com -d yourdomain.com -f
```

如使用过程有任何问题，欢迎issue。
