# thirdparty-notice-generator

[![GitHub license](https://img.shields.io/badge/license-MIT-green.svg)]()

## ThirdPartyNotice自動生成ツール
自動でプロジェクトに含まれてるライブラリのライセンス情報を収集するやつ

## インストール
```
uv tool install git+https://github.com/futa-t/thirdparty-notice-generator 
```

## 使い方
```
Usage: thirdparty-notice-generator <projectfile> [<outputfile>]
```

```
thirdparty-notice-generator ./pyproject.toml ThirdPartyNotice.txt
```

- 対応してるやつ
    - C#(.NET) - *.csproj, *.sln
    - Python - pyproject.toml

## TODO
- Rust(Cargo.toml)の対応
- ヘッダーとかのテンプレート設定
- 差分更新