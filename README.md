# 江苏省铁路集团造价审价中心工作平台 - Android APK

## 项目说明

这是一个基于 **Chaquopy** (Python in Android) 的 Android 应用，将 Flask Web 平台打包为独立的 Android APK。

## 技术栈

- **Android**: Java + WebView
- **Python**: Flask 3.0 + SQLAlchemy + Flask-Login
- **打包工具**: Chaquopy 15.0.1
- **构建工具**: Gradle + GitHub Actions

## 功能模块

1. 制度标准管理
2. 造价审价（项目审核）
3. 费用审核
4. 资金管理（拨付/验工）
5. 招招标合同审核
6. 数据总览/统计
7. 审核记录
8. 问题库
9. 任务管理

## 默认账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 系统管理员 |

## 构建方式

### 方式一：GitHub Actions 自动编译（推荐）

1. Fork 此仓库到您的 GitHub 账号
2. 进入仓库的 **Actions** 页面
3. 选择 **Build Android APK** → **Run workflow**
4. 等待约 5-10 分钟完成
5. 在 **Artifacts** 中下载 `RailwayPlatform-APK` → 内含 `app-debug.apk`
6. 将 APK 安装到 Android 手机即可使用

### 方式二：本地 Android Studio 编译

1. 安装 [Android Studio](https://developer.android.com/studio)
2. 用 Android Studio 打开此项目目录
3. 等待 Gradle 同步完成（首次需要下载 SDK）
4. 菜单 Build → Build Bundle(s) / APK(s) → Build APK(s)
5. APK 输出在: `app/build/outputs/apk/debug/app-debug.apk`

## 项目结构

```
railway_android/
├── app/
│   ├── build.gradle              # Chaquopy + Flask 配置
│   ├── src/main/
│   │   ├── AndroidManifest.xml
│   │   ├── java/com/railway/platform/
│   │   │   └── MainActivity.java # 启动Flask + WebView
│   │   └── res/                 # 图标、布局、样式
│   └── proguard-rules.pro
├── python/app/                   # Python Flask 源码
│   ├── app.py                    # Flask应用工厂 + 所有路由
│   ├── run_app.py                # 入口(被Java调用)
│   ├── config.py                 # 配置
│   ├── extensions.py             # DB/Login扩展
│   └── models.py                 # 数据模型
├── .github/workflows/
│   └── build-apk.yml            # GitHub Actions 构建配置
├── build.gradle                  # 项目级构建配置
├── settings.gradle
└── gradle.properties
```

## 注意事项

- 本地数据库存储在手机内部存储，数据不与电脑端同步
- 首次启动会自动创建管理员账号 (admin/admin123)
- 需要 Android 7.0+ (API 24+)

## License

© 2026 江苏省铁路集团造价审价中心
