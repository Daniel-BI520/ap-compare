"""
为AP数据库补充电口/光口上行数量字段
"""
import json
import copy

input_file = '/Coze/Drive/友商交换机分析/ap-compare/ap_data.json'

with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

products = data['products']

# ============================================================
# 带光口型号的电口/光口映射表
# 格式: model_full_name -> (electrical_count, optical_count, note, verified)
# verified=False 表示待核实
# ============================================================

uplink_map = {
    # ===== 华为 (19款) =====
    "AirEngine 8776-X7THP-T": (2, 1, "1个独立10GE电 + 1对combo(10GE电/光) + GE下行", True),
    "AirEngine 8771-X1T": (2, 1, "1个独立10GE电 + 1对combo(10GE电/光)", True),
    "AirEngine 8760-X1-PRO": (2, 1, "1个独立10GE电 + 1对combo(10GE电/光) + GE下行", True),
    "AirEngine 6776-X7TH": (2, 1, "1个独立10GE电 + 1对combo(10GE电/光) + GE下行", True),
    "AirEngine 6776-X6H": (2, 1, "1个独立5GE电 + 1对combo(5GE电/10GE光) + GE下行", True),
    "AirEngine 6776-X6ETH": (2, 1, "1个独立5GE电 + 1对combo(5GE电/10GE光) + GE下行", True),
    "AirEngine 6760-X1": (2, 1, "1个独立10GE电 + 1对combo(10GE电/10GE SFP+光) + GE下行", True),
    "AirEngine 6761-21": (1, 1, "1对combo(2.5GE电/10GE SFP+光)，二选一", True),
    "AirEngine 5773-25HW": (1, 1, "面板AP，1个2.5GE电上行 + 1个2.5GE光上行 + 8GE下行", True),
    "AirEngine 5773-21HW": (0, 1, "面板AP，纯光上行：1个2.5GE光口 + 4GE下行", True),
    "AirEngine 5773-23HW": (1, 1, "面板AP，1个2.5G光口 + 1个GE电上行 + 3GE下行（待确认）", False),
    "AirEngine 8776I-X6ETHP-T": (2, 1, "室外AP，1个独立10GE电 + 1对combo(10GE电/光) + GE下行", True),
    "AirEngine 8760R-X1": (2, 1, "室外AP，1个独立10GE电 + 1对combo(10GE电/光) + GE下行", True),
    "AirEngine 6776I-X7TH": (2, 1, "室外AP，1个独立10GE电 + 1对combo(10GE电/光) + GE下行", True),
    "AirEngine 6760R-51": (2, 1, "室外AP，1个独立5GE电 + 1对combo(5GE电/10GE SFP+光) + GE下行", True),
    "AirEngine 5776I-X6H": (1, 1, "室外AP，1个10GE光口 + 1个2.5GE电口，双上行", True),
    "AirEngine 5761R-11": (1, 1, "室外AP，1个GE电口 + 1个GE光口（combo）", True),
    "AirEngine 9700D-M1 万兆中心AP": (0, 4, "中心AP，4个10GE SFP+光口上行", True),
    "AirEngine 9700D-S 分布式接入点": (2, 1, "分布式AP，2个2.5GE电上行 + 1个10GE光上行", True),

    # ===== H3C (19款) =====
    "H3C WA7638": (2, 1, "1个独立10GE电 + 1对combo(10GE电/10GE PSFP光) + GE下行", True),
    "H3C WA7538": (1, 1, "1对combo(10GE电/10GE PSFP光) + GE/PSE下行", True),
    "H3C WA7338-HI": (1, 1, "1对combo(10GE电/10GE PSFP光)", True),
    "H3C WA7330i": (1, 1, "1对combo(10GE电/10GE PSFP光)，二选一", True),
    "H3C WA7320i": (1, 1, "1个10GE电上行 + 1个10G PSFP光上行 + GE/PSE下行", True),
    "H3C WA7636": (1, 1, "1个2.5GE电 + 1个10GE PSFP光（combo），待核实", False),
    "H3C WA7539": (1, 1, "1对combo(10GE电/10GE PSFP光)", True),
    "H3C WA6638i": (2, 1, "1个独立10GE电 + 1对combo(10GE电/10GE SFP+光) + GE下行", True),
    "H3C WA6638": (3, 0, "⚠️ 原数据标记有光口，但官网/第三方参数显示仅2电口（10GE+GE），疑似无光口，待核实", False),
    "H3C WA6636": (3, 0, "⚠️ 原数据标记有光口，但官网规格显示3电口（10GE+2GE）全电口，无光口，待核实", False),
    "H3C WA6520": (1, 1, "1个GE电口 + 1个2.5G/1G光口", True),
    "H3C WA6520-HI": (2, 0, "⚠️ 原数据标记有光口且count=1，但官网规格为2电口（2.5GE+GE），无光口，待核实", False),
    "H3C WA6520H": (1, 0, "⚠️ 面板型，原数据count=1有光口，但官网规格为1电口上行+下行电口，无光口，待核实", False),
    "H3C WA6526H": (1, 0, "⚠️ 面板型，原数据标记有光口，但官网规格为1个2.5GE电口上行，无光口，待核实", False),
    "H3C WA6520X-E": (1, 1, "室外AP，1个GE电 + 1个2.5G光口（待确认具体速率）", True),
    "H3C WA7220X": (1, 1, "室外AP，1个2.5GE电 + 1个10GE PSFP光", True),
    "H3C WA7630X": (1, 1, "室外AP，1个10GE电 + 1个10GE SFP+光 + GE/PSE下行", True),
    "H3C WA7330X": (1, 1, "室外AP，1个10GE电 + 1个10GE PSFP光 + GE/PSE下行", True),
    "H3C WTU720 多业务分布式AP": (1, 0, "⚠️ 原数据标记有光口且speed=10000，但官网规格为2电口（2.5GE），无光口速率也是2.5G，数据存疑", False),

    # ===== 锐捷 (22款) =====
    "RG-AP9861-R": (2, 1, "1个独立10GE电 + 1对combo(10GE电/10GE SFP+光) + GE下行", True),
    "RG-AP9850-R": (2, 1, "1个独立10GE电 + 1对combo(10GE电/10GE SFP+光) + GE下行", True),
    "RG-AP9751-R": (2, 1, "1个独立10GE电 + 1对combo(10GE电/10GE SFP+光) + GE下行", True),
    "RG-AP9520-RDX": (1, 1, "1对combo(5GE电/10GE SFP+光) + GE下行", True),
    "RG-AP9250-R": (1, 1, "1对combo(5GE电/10GE SFP+光)", True),
    "RG-AP9220-R": (1, 1, "1个2.5GE电 + 1个2.5GE SFP光", True),
    "RG-AP9220(V2)": (1, 1, "1个2.5GE电 + 1个5G SFP光", True),
    "RG-AP880-AR": (2, 1, "1个独立5GE电 + 1对combo(5GE电/光) + GE下行", True),
    "RG-AP680-AR": (1, 2, "1个5GE电 + 2个10GE SFP+光口", True),
    "RG-AP680C": (1, 1, "1个GE电 + 1个GE SFP光", True),
    "RG-AP680-A": (1, 1, "1个GE电 + 1个GE SFP光", True),
    "RG-APD4930 零漫游主机AP": (3, 2, "零漫游主机，3个GE电上行 + 2个2.5GE SFP光上行 + 1GE下行", True),
    "RG-AP6920-D": (1, 1, "室外AP，1个2.5GE电 + 1个2.5GE SFP光口（原speed=10000存疑）", False),
    "RG-AP7176-R(V2)": (1, 1, "1对combo(10GE电/10GE SFP+光)", True),
    "RG-AP6981": (1, 1, "1对combo(10GE电/10GE SFP+光)，Wi-Fi 7室外/放装型", True),
    "RG-AP680-IO": (1, 1, "室外AP，1个5GE电 + 1个10GE SFP+光 + GE下联", True),
    "RG-AP850-I": (1, 0, "⚠️ 原数据标记有光口，但官网规格为全电口（2GE上行+1GE下行），无光口，待核实", False),
    "RG-AP850(TR)": (2, 0, "⚠️ 原数据标记有光口，但参考同系列850(AR)为全电口，疑似无光口，待核实", False),
    "RG-AP850-AR(V3)": (1, 1, "1对combo(5GE电/5GE SFP光) + GE下联", True),
    "RG-AP840-I(V2)": (1, 1, "1对combo(5GE电/5GE SFP光) + GE下联", True),
    "RG-AM5532 智分+主机": (4, 4, "智分+主机，4个GE电上行 + 4个10GE SFP+光上行（支持三种模式：4光/4电/2光2电）", True),
    "RG-AM5528(ES) 智分+主机": (2, 2, "智分+主机，2个GE电上行 + 2个10GE SFP+光上行", True),
}

# ============================================================
# 写入数据
# ============================================================
updated_count = 0
verification_data = []

for p in products:
    model = p['model_full_name']
    has_opt = p['has_optical_uplink']
    orig_count = p['uplink_port_count']
    
    if has_opt:
        if model in uplink_map:
            elec, opt, note, verified = uplink_map[model]
            p['uplink_electrical_count'] = elec
            p['uplink_optical_count'] = opt
            
            verification_data.append({
                'model': model,
                'vendor': p['vendor'],
                'orig_count': orig_count,
                'orig_speed': p['uplink_port_speed'],
                'new_electrical': elec,
                'new_optical': opt,
                'total_physical': elec + opt,
                'note': note,
                'verified': verified
            })
            updated_count += 1
        else:
            # 未找到映射，默认填1光口，电口=count-1
            p['uplink_electrical_count'] = max(0, orig_count - 1)
            p['uplink_optical_count'] = 1
            verification_data.append({
                'model': model,
                'vendor': p['vendor'],
                'orig_count': orig_count,
                'orig_speed': p['uplink_port_speed'],
                'new_electrical': max(0, orig_count - 1),
                'new_optical': 1,
                'total_physical': orig_count,
                'note': '未找到匹配，默认填充',
                'verified': False
            })
            updated_count += 1
    else:
        # 无光口型号：全部为电口
        p['uplink_electrical_count'] = orig_count
        p['uplink_optical_count'] = 0
        updated_count += 1

# 保存
with open(input_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"完成更新：共 {updated_count} 款产品")
print(f"带光口：{len([v for v in verification_data if v['new_optical'] > 0])} 款")
print(f"已核实：{len([v for v in verification_data if v['verified']])} 款")
print(f"待核实：{len([v for v in verification_data if not v['verified']])} 款")

# 按厂商统计
from collections import Counter
vendor_stats = Counter()
for v in verification_data:
    vendor_stats[v['vendor']] += 1
print("\n按厂商分布：")
for v, c in vendor_stats.items():
    verified = len([x for x in verification_data if x['vendor']==v and x['verified']])
    pending = c - verified
    print(f"  {v}: {c}款 (已核实{verified}, 待核实{pending})")

# 输出待核实清单
print("\n===== 待核实型号清单 =====")
for v in verification_data:
    if not v['verified']:
        print(f"  [{v['vendor']}] {v['model']}")
        print(f"    原配置: count={v['orig_count']}, speed={v['orig_speed']}")
        print(f"    新配置: 电{v['new_electrical']} + 光{v['new_optical']} = {v['total_physical']}")
        print(f"    备注: {v['note']}")
