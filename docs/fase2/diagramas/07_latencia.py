import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.family"]="DejaVu Sans"
cats=["Render + Supabase\nantes del ajuste","Render + Supabase\ndespués del ajuste","AWS EC2\n(misma máquina)"]
prom=[1903,1577,216]; p95=[2198,1879,300]
S1,S2="#2a78d6","#eb6834"; TXT="#0b0b0b"; TX2="#52514e"; SURF="#fcfcfb"
fig,ax=plt.subplots(figsize=(9,5.2),dpi=200); fig.patch.set_facecolor(SURF); ax.set_facecolor(SURF)
import numpy as np
x=np.arange(3); w=0.34
b1=ax.bar(x-w/2-0.01,prom,w,color=S1,label="Promedio",zorder=3)
b2=ax.bar(x+w/2+0.01,p95,w,color=S2,label="Percentil 95",zorder=3)
for bars in (b1,b2):
    for b in bars:
        ax.text(b.get_x()+b.get_width()/2,b.get_height()+35,f"{int(b.get_height()):,}".replace(",","."),ha="center",va="bottom",fontsize=9,color=TXT)
ax.axhline(1000,color=TX2,lw=1.2,ls=(0,(4,3)),zorder=2)
ax.text(2.55,1030,"Meta: 1.000 ms",ha="right",va="bottom",fontsize=9,color=TX2)
ax.set_xticks(x); ax.set_xticklabels(cats,fontsize=9.5,color=TXT)
ax.set_ylabel("Tiempo hasta que la alerta llega al panel (ms)",fontsize=9.5,color=TX2)
ax.set_ylim(0,2500)
ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v,p:f"{int(v):,}".replace(",",".")))
ax.grid(axis="y",color="#e4e3df",lw=0.8,zorder=0)
for s in ["top","right","left"]: ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#c9c8c3"); ax.tick_params(axis="y",colors=TX2,labelsize=9,length=0); ax.tick_params(axis="x",length=0)
ax.legend(frameon=False,fontsize=9,loc="upper right")
ax.set_title("PR-01 y PR-01b · Latencia de la alerta crítica (30 caídas por escenario)",fontsize=11.5,color=TXT,loc="left",pad=14,fontweight="bold")
fig.text(0.01,0.01,"Fuente: registro_pruebas.md (02-10-2026). 30/30 alertas recibidas en los tres escenarios.",fontsize=8,color=TX2)
plt.tight_layout(rect=(0,0.03,1,1)); plt.savefig("07_latencia_pr01.png",facecolor=SURF)
