"""
TBH: Task Bar Hero — Bot de Automação

Uso:
    python main.py --gui                         # Interface gráfica
    python main.py --stage 2-4                   # Navega uma vez para o estágio 2-4
    python main.py --farm exp_farm               # Loop com preset
    python main.py --farm 1-7,1-8 --loop        # Lista customizada, infinito
    python main.py --farm 1-7,1-8 --iterations 5
    python main.py --list-stages                 # Lista todos os estágios
    python main.py --list-presets                # Lista presets de farm
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from tbh.config import Config
from tbh.utils import setup_logging
from tbh import build_navigator


def parse_args():
    parser = argparse.ArgumentParser(
        description="TBH Task Bar Hero — Automação de Mapas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--gui", action="store_true", help="Abrir interface gráfica")
    mode.add_argument("--stage", metavar="ID", help="Navegar uma vez para o estágio (ex: 2-4)")
    mode.add_argument("--farm", metavar="PRESET_OU_LISTA", help="Farm loop: nome de preset ou lista separada por vírgula (ex: 1-7,1-8)")
    mode.add_argument("--list-stages", action="store_true", help="Listar todos os estágios disponíveis")
    mode.add_argument("--list-presets", action="store_true", help="Listar presets de farm")

    parser.add_argument("--loop", action="store_true", help="Repetir indefinidamente (para --farm)")
    parser.add_argument("--iterations", type=int, default=1, help="Número de iterações para --farm (padrão: 1)")
    parser.add_argument("--debug", action="store_true", help="Ativar logs de debug")
    return parser.parse_args()


def main():
    args = parse_args()
    logger = setup_logging(args.debug)

    config = Config.load(base_dir=ROOT)

    if args.list_stages:
        for act_key, act in config.acts.items():
            print(f"\n{act.label}:")
            for stage in act.stages:
                print(f"  {stage.id:<6} {stage.label}")
        return

    if args.list_presets:
        print("\nPresets de farm disponíveis:")
        for name, stages in config.farm_presets.items():
            print(f"  {name:<20} → {', '.join(stages)}")
        return

    if args.gui or (not args.stage and not args.farm):
        from gui.app import AutomationApp
        app = AutomationApp(config)
        app.mainloop()
        return

    navigator = build_navigator(config)

    if args.stage:
        logger.info(f"Navegando para estágio {args.stage}...")
        navigator.navigate_to(args.stage)
        logger.info("Concluído.")
        return

    if args.farm:
        # Resolve preset ou lista de estágios
        if args.farm in config.farm_presets:
            stage_ids = config.get_farm_preset(args.farm)
            logger.info(f"Usando preset '{args.farm}': {stage_ids}")
        else:
            stage_ids = [s.strip() for s in args.farm.split(",") if s.strip()]

        if not stage_ids:
            print("Nenhum estágio especificado.")
            sys.exit(1)

        iterations = None if args.loop else args.iterations
        loop_desc = "infinito" if iterations is None else f"{iterations}x"
        logger.info(f"Iniciando farm loop: {stage_ids} — {loop_desc}")
        navigator.farm_loop(stage_ids, iterations=iterations)


if __name__ == "__main__":
    main()
