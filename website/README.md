# PACE Lab 网站

这是 PaceLab 资料库中的公共网站子项目。

网站使用 [Quarto](https://quarto.org/) 构建。只有本目录中的内容会进入网站构建和发布流程；仓库中的课题组手册不会自动出现在网站上。

## 编辑网站

主要文件包括：

- `index.qmd`：首页与课题组简介
- `research.qmd`：研究方向
- `people.qmd`：成员信息
- `publications.qmd`：发表论文
- `contact.qmd`：联系方式
- `_quarto.yml`：导航、页脚和全站设置
- `pace-site.css`：视觉样式

在本目录中预览网站：

```sh
quarto preview
```

构建网站：

```sh
quarto render
```

生成的网站保存在 `website/_site/`。

## 发布

GitHub Pages 工作流位于仓库根目录的 `.github/workflows/pages.yml`，只在网站子项目或工作流本身发生变化时运行。

如使用 Cloudflare Pages：

1. 将项目的根目录设置为 `website`；
2. 将构建命令设置为 `bash scripts/cloudflare-build.sh`；
3. 将输出目录设置为 `_site`。

## 发布前检查

正式发布学校、院系、办公地址或其他机构信息前，请确认这些信息准确且适合公开。
