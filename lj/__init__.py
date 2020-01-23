__VERSION__ = (1, 0, 0)

# __init__ 不要放外部依赖 避免在安装依赖之前导入了外部依赖
if __name__ == "__main__":
    from lj.lj import lj_main

    lj_main()
