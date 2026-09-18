"""Record or evaluate a paired task test using a downloaded hypothesis review."""
import argparse
import json
from pathlib import Path
from jsonschema import ValidationError
from experiment import plan_test, check_plan, evaluate_test
from validate_decisions import read_json


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--review',required=True,type=Path)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--fields',type=Path)
    group.add_argument('--plan',type=Path)
    parser.add_argument('--observations',type=Path)
    parser.add_argument('--output-dir',required=True,type=Path)
    args=parser.parse_args()
    try:
        if args.output_dir.exists():raise ValueError('Choose a new output directory; previous work is never overwritten.')
        package=read_json(args.review)
        if not isinstance(package,dict) or package.get('kind')!='market-hypothesis-review':
            raise ValueError('Provide an exported hypothesis review JSON.')
        context=[package[key] for key in ('analysis','decisions','review')]
        plan=plan_test(*context,read_json(args.fields)) if args.fields else check_plan(*context,read_json(args.plan))
        result=None
        if args.observations:
            if args.observations.stat().st_size>800_000:raise ValueError('Observation file exceeds the local size limit.')
            result=evaluate_test(*context,plan,args.observations.read_text(encoding='utf-8-sig'))
        args.output_dir.mkdir(parents=True,exist_ok=False)
        (args.output_dir/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        if result:
            (args.output_dir/'result.json').write_text(json.dumps(result['package'],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            (args.output_dir/'result.md').write_text(result['markdown'],encoding='utf-8')
        print(json.dumps({'status':'ok','plan_id':plan['plan_id'],'result':result['package']['result'] if result else None}))
        return 0
    except (ValueError,ValidationError,OSError,KeyError,TypeError) as error:
        print(json.dumps({'status':'error','message':str(error) if isinstance(error,ValueError) else 'Check the documented file format and paths.'}))
        return 2


if __name__=='__main__':raise SystemExit(main())
