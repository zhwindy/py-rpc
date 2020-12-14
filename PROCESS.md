## 进程管理相关知识

### fork进程
操作系统的fork系统调用,用于父进程创建子进程.
fork()方法有2个返回值: 
    1. 在父进程中返回子进程的进程id
    2. 在子进程中返回0

### 结束(杀死)子进程
* 子进程正常结束
子进程运行结束后,需要由父进程调用waitpid来终止。
如果父进程不终止子进程,则子进程变成僵尸进程,一直占用系统资源,直到父进程结束后随父进程退出。

* 向进程发送终止信号
向进程发送终止信号SINGKILL,SIGINT,或SIGTERM均可以结束子进程

### 进程信号处理函数
进程内部定义了信号处理函数,当收到信号时(终止信号或者其他信号),执行处理函数.

可以捕获特定的信号,覆盖默认的处理行为.比如SIGINT信号默认的处理行为是退出进程,可以修改SIGINT的处理函数使其不退出.

### 常用进程信号
1. `SIGINT` 退出进程,当在键盘上`Ctrl + c`时就是向进程发送SIGINT信号;
2. `SIGKILL` 当使用`kill -9`杀死进程时,暴力杀进程,无法捕获,只能使进程暴力退出;
3. `SIGTERM` 当使用`kill`不带参数杀死进程时,进程会收到此信号,默认退出进程,可以自定义覆盖默认处理函数;
4. `SIGCHILD` 子进程退出时,父进程会收到此信号。子进程退出后,父进程必须通过waitpid收割子进程,否则子进程会变成僵尸;

### 常见系统错误码
python的errono定义了大多常见的系统调用错误码
1. `errono.EPERM`-`Operation not permitted`
2. `errono.ENOENT`-`No such file or directory`
3. `errono.ESRCH`-`No such process`
4. `errono.EINTR`-`Interrupted system call` 调用被打断,遇到此错误一般需要重试
5. `errono.EIO`-`I/O error`
6. `errono.EBADF`-`Bad file number`
7. `errono.ECHILD`-`No child processes` 子进程不存在,当waitpid收割子进程时,目标进程不存在,就会报此错误

### 收割子进程
收割子进程使用`waitpid(pid, options)`系统调用
* pid 指定子进程的id, pid=-1代表任意子进程
* options
    1. 0 表示阻塞,等待子进程结束后才返回
    2. WHOHANG 表示非阻塞,有则返回pid,否则返回0
* 异常
    1. 如果指定收割的进程不存在,则会报异常 `OSError`-`errono.ECHILD`
    2. 若收割过程中被中断,则异常`OSError`-`errono.EINTR`

### 父进程退出
父进程退出时,要先关闭所有的子进程。否则父进程退出后,子进程仍然运行.
```
import os
import signal

for pid in pids:
    os.kill(pid, signal.SIGTERM)

for pid in pids:
    os.waitpid(pid, os.WHOHANG)
sys.exit(0)
```

### 信号连续打断
当进程收到信号执行信号处理函数时,又被其他信号打断,则执行新到的处理函数,处理完成后依次返回继续处理