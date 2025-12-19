import csv
import os
import sys
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 设置页面配置
st.set_page_config(
    page_title="1999-2023年企业数字化转型指数查询系统",
    page_icon="📊",
    layout="wide"
)

class IndexQueryApp:
    def __init__(self):
        self.data = []
        self.keyword_stats = []
        self.companies = []
        self.stock_codes = []
        self.years = []
        self.load_data()
        self.main()

    def load_data(self):
        """加载CSV数据"""
        st.info("正在加载数据...")
        # 获取当前目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 加载数字化转型指数结果表
        index_file = os.path.join(current_dir, "1999-2023年数字化转型指数结果表.csv")
        
        if not os.path.exists(index_file):
            st.error(f"找不到数据文件: {index_file}")
            return
        
        try:
            # 使用utf-8-sig编码处理BOM
            with open(index_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                self.data = list(reader)
            
            st.success(f"数字化转型指数数据加载完成，共 {len(self.data)} 条记录")
            
            if self.data:
                # 提取企业列表、股票代码列表和年份列表
                self.companies = sorted(list(set(row['企业名称'] for row in self.data)))
                self.stock_codes = sorted(list(set(row['股票代码'] for row in self.data)))
                self.years = sorted(list(set(int(row['年份']) for row in self.data)))
                
                # 转换数值字段为float
                for row in self.data:
                    row['年份'] = int(row['年份'])
                    row['数字化转型指数(0-100分)'] = float(row['数字化转型指数(0-100分)'])
                    row['人工智能词频数'] = int(row['人工智能词频数'])
                    row['大数据词频数'] = int(row['大数据词频数'])
                    row['云计算词频数'] = int(row['云计算词频数'])
                    row['区块链词频数'] = int(row['区块链词频数'])
                    row['数字技术运用词频数'] = int(row['数字技术运用词频数'])
                    row['总词频数'] = int(row['总词频数'])
        except Exception as e:
            st.error(f"数字化转型指数数据加载失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return
        
        # 加载年报技术关键词统计
        keyword_file = os.path.join(current_dir, "1999-2023年年报技术关键词统计.csv")
        
        if os.path.exists(keyword_file):
            try:
                with open(keyword_file, 'r', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    self.keyword_stats = list(reader)
                
                st.success(f"年报技术关键词统计数据加载完成，共 {len(self.keyword_stats)} 条记录")
            except Exception as e:
                st.error(f"年报技术关键词统计数据加载失败: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            st.info(f"未找到年报技术关键词统计文件: {keyword_file}")

    def main(self):
        """主界面"""
        st.title("1999-2023年企业数字化转型指数查询系统")
        
        # 创建查询面板
        with st.container():
            st.subheader("查询条件")
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                query_type = st.radio("查询类型", ["企业名称", "股票代码"])                
                if query_type == "企业名称":
                    company = st.selectbox("企业名称", options=["全部"] + self.companies)
                    stock_code = "全部"
                else:
                    stock_code = st.selectbox("股票代码", options=["全部"] + self.stock_codes)
                    company = "全部"
            
            with col2:
                if self.years:
                    # 使用selectbox替代slider，让用户直接选择年份范围
                    start_year = st.selectbox(
                        "开始年份",
                        options=self.years,
                        index=0
                    )
                    end_year = st.selectbox(
                        "结束年份",
                        options=self.years,
                        index=len(self.years)-1
                    )
                else:
                    start_year = 1999
                    end_year = 2023
                    st.info("数据加载中，默认年份范围1999-2023")
            
            # 移除查询按钮，实现自动更新
        
        # 自动更新图表，不需要点击查询按钮
        if start_year > end_year:
            st.warning("开始年份不能大于结束年份")
            return
        
        # 过滤数据
        filtered_data = []
        for row in self.data:
            if (company == "全部" or row['企业名称'] == company) and \
               (stock_code == "全部" or row['股票代码'] == stock_code) and \
               start_year <= row['年份'] <= end_year:
                filtered_data.append(row)
        
        if not filtered_data:
            st.info("没有找到符合条件的数据")
            return
        
        st.success(f"找到 {len(filtered_data)} 条记录")
        
        # 创建结果选项卡
        tab1, tab2, tab3 = st.tabs(["指数趋势", "关键词分析", "详细数据"])
        
        with tab1:
            self.update_trend_tab(filtered_data)
        
        with tab2:
            self.update_keyword_tab(filtered_data)
        
        with tab3:
            self.update_detail_tab(filtered_data)
            self.update_stats_tab(filtered_data)

    def update_trend_tab(self, data):
        """更新指数趋势图"""
        st.subheader("数字化转型指数趋势")
        
        # 按年份排序
        sorted_data = sorted(data, key=lambda x: x['年份'])
        
        # 准备数据
        years = [row['年份'] for row in sorted_data]
        indices = [row['数字化转型指数(0-100分)'] for row in sorted_data]
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 绘制折线图
        ax.plot(years, indices, marker='o', linestyle='-', linewidth=2, markersize=6, color='#1f77b4')
        
        # 设置图表属性
        ax.set_title('数字化转型指数趋势', fontsize=14, fontweight='bold')
        ax.set_xlabel('年份', fontsize=12)
        ax.set_ylabel('数字化转型指数(0-100分)', fontsize=12)
        
        # 自动定位到选择的年份范围
        if years:
            ax.set_xlim(min(years), max(years))
            
            # 设置x轴刻度为整数年份
            ax.set_xticks(years)
            ax.tick_params(axis='x', rotation=45)
        
        # 设置y轴范围
        ax.set_ylim(0, 100)
        
        # 添加网格线
        ax.grid(True, alpha=0.3)
        
        # 显示图表
        st.pyplot(fig)

    def update_keyword_tab(self, data):
        """更新关键词分析图"""
        st.subheader("关键词分析")
        
        # 按年份排序
        sorted_data = sorted(data, key=lambda x: x['年份'])
        
        # 准备数据
        years = [row['年份'] for row in sorted_data]
        ai_counts = [row['人工智能词频数'] for row in sorted_data]
        bigdata_counts = [row['大数据词频数'] for row in sorted_data]
        cloud_counts = [row['云计算词频数'] for row in sorted_data]
        blockchain_counts = [row['区块链词频数'] for row in sorted_data]
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 使用英文标签避免中文显示问题
        labels = ['AI', 'Big Data', 'Cloud', 'Blockchain']
        colors = ['red', 'blue', 'green', 'purple']
        
        # 绘制堆叠柱状图
        ax.bar(years, ai_counts, label=labels[0], color=colors[0])
        ax.bar(years, bigdata_counts, bottom=ai_counts, label=labels[1], color=colors[1])
        ax.bar(years, cloud_counts, bottom=[sum(x) for x in zip(ai_counts, bigdata_counts)], label=labels[2], color=colors[2])
        ax.bar(years, blockchain_counts, bottom=[sum(x) for x in zip(ai_counts, bigdata_counts, cloud_counts)], label=labels[3], color=colors[3])
        
        # 设置图表属性
        ax.set_title('Keyword Usage Trend')
        ax.set_xlabel('Year')
        ax.set_ylabel('Frequency')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # 显示图表
        st.pyplot(fig)

    def update_detail_tab(self, data):
        """更新详细数据表格"""
        st.subheader("详细数据")
        
        # 转换为DataFrame以便显示
        df = pd.DataFrame(data)
        
        # 设置显示的列顺序
        columns = ['企业名称', '股票代码', '年份', '数字化转型指数(0-100分)', 
                  '人工智能词频数', '大数据词频数', '云计算词频数', '区块链词频数', 
                  '数字技术运用词频数', '总词频数']
        
        # 显示数据表格
        st.dataframe(df[columns], height=400)

    def update_stats_tab(self, data):
        """更新统计信息"""
        st.subheader("统计信息")
        
        # 计算基本统计
        total_records = len(data)
        companies = sorted(list(set(row['企业名称'] for row in data)))
        years = sorted(list(set(row['年份'] for row in data)))
        
        # 计算指数统计
        indices = [row['数字化转型指数(0-100分)'] for row in data]
        avg_index = sum(indices) / len(indices) if indices else 0
        max_index = max(indices) if indices else 0
        min_index = min(indices) if indices else 0
        
        # 计算关键词统计
        keywords = {
            '人工智能': sum(row['人工智能词频数'] for row in data),
            '大数据': sum(row['大数据词频数'] for row in data),
            '云计算': sum(row['云计算词频数'] for row in data),
            '区块链': sum(row['区块链词频数'] for row in data)
        }
        
        # 计算数字技术运用和总词频数统计
        tech_usage = sum(row['数字技术运用词频数'] for row in data)
        total_words = sum(row['总词频数'] for row in data)
        
        # 创建统计卡片
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("总记录数", total_records)
            st.metric("企业数量", len(companies))
            st.metric("年份范围", f"{min(years)} - {max(years)}" if years else "无")
        
        with col2:
            st.metric("平均指数", f"{avg_index:.2f}")
            st.metric("最高指数", f"{max_index:.2f}")
            st.metric("最低指数", f"{min_index:.2f}")
        
        with col3:
            st.metric("人工智能词频", keywords['人工智能'])
            st.metric("大数据词频", keywords['大数据'])
            st.metric("云计算词频", keywords['云计算'])
            st.metric("区块链词频", keywords['区块链'])
        
        # 显示更多统计信息
        st.divider()
        st.markdown(f"**数字技术运用总词频**: {tech_usage} 次")
        st.markdown(f"**总词频数**: {total_words} 次")
        
        # 详细展示年报技术关键词统计数据
        if self.keyword_stats:
            st.divider()
            st.subheader("年报技术关键词统计")
            st.markdown(f"  共 {len(self.keyword_stats)} 条年度统计记录")
            
            # 计算年报技术关键词的统计数据
            total_tech_keywords = 0
            yearly_stats = {}
            
            for row in self.keyword_stats:
                # 尝试获取年份和关键词数据
                try:
                    year = row.get('年份', '未知')
                    keyword_count = int(row.get('数字技术词频数', 0))
                    total_tech_keywords += keyword_count
                    
                    # 按年份统计
                    if year not in yearly_stats:
                        yearly_stats[year] = 0
                    yearly_stats[year] += keyword_count
                except:
                    continue
            
            st.markdown(f"  年报技术关键词总词频数: {total_tech_keywords} 次")
            
            if yearly_stats:
                st.markdown("  各年度年报技术关键词使用情况:")
                
                # 创建年度统计表格
                yearly_df = pd.DataFrame(list(yearly_stats.items()), columns=['年份', '词频数'])
                yearly_df = yearly_df.sort_values('年份')
                
                st.dataframe(yearly_df, height=200)

# 运行应用
if __name__ == "__main__":
    app = IndexQueryApp()