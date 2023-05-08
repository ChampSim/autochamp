import os

header_fmtstr = '''#!/bin/bash
#SBATCH --get-user-env=L
#SBATCH --time={limit_hours}:00:00
#SBATCH --ntasks={ntasks}
#SBATCH --mem=1024M
#SBATCH --mail-type=FAIL
#SBATCH --mail-user={mail}
#SBATCH --account={account}
'''

'''
#SBATCH --job-name={output_name}
#SBATCH --output={result_str}.%j
'''

def run(runs, env_con):
    with open(env_con.fields['launch_file'], 'w') as launch_file:
        launch_file.write(header_fmtstr.format(**env_con.fields))
        launch_file.write('#SBATCH --array=1-{}%{}\n'.format(len(runs), env_con.fields['job_limit']))

        launch_file.write('sed -n "$SLURM_ARRAY_TASK_ID p" <<EOF\n')
        for r in runs:
            launch_file.write(' '.join(r) + '\n')
        launch_file.write('EOF | bash\n')

    print("Running command:", "sbatch", env_con.fields["launch_file"])
    os.system('sbatch '+env_con.fields['launch_file'])
