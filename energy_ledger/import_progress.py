"""User-facing import stages, derived only from durable processing state."""
import json


def detail_object(value):
    if isinstance(value, dict):
        return value
    try:
        result = json.loads(value or '{}')
        return result if isinstance(result, dict) else {}
    except (ValueError, TypeError):
        return {}


def import_progress(job, pipeline=None):
    state = job['state']
    result = {'step': 1, 'total_steps': 4, 'level': 'working', 'terminal': False,
              'label': 'PDF je sprejet; čakam na branje in preverjanje računa.',
              'error_code': None, 'next_attempt_at': None}
    if state in {'REJECTED', 'REVIEW', 'CONFLICT'}:
        detail = detail_object(job.get('detail'))
        result.update(level='error', terminal=True, label={
            'REJECTED': 'Računa ni mogoče obdelati. Preveri PDF in podatke na računu.',
            'REVIEW': 'Račun potrebuje pregled; podatki niso samodejno potrjeni.',
            'CONFLICT': 'Račun je v konfliktu z že shranjenim računom.'}[state],
            error_code=detail.get('detail') or detail.get('error') or state)
        return result
    if state != 'VALID':
        return result
    result.update(step=2, label='Račun je prebran. Čakam na podatke Moj Elektro in primerjavo.')
    if not pipeline:
        return result
    stage = pipeline['state']
    if stage == 'RUNNING':
        result.update(step=2, label='Pridobivam podatke Moj Elektro in preverjam skladnost računa.')
    elif stage == 'COMPLETE':
        dimensions = detail_object(pipeline.get('detail')).get('reconciliation', {}).get('dimensions', {})
        mismatch = 'FAIL' in dimensions.values()
        result.update(step=4, level='warning' if mismatch else 'success', terminal=True,
                      label='Obdelava je zaključena, vendar račun odstopa od meritev. Preveri primerjavo.'
                      if mismatch else 'Račun je obdelan in primerjava z Moj Elektro je zaključena.')
    elif stage in {'ERROR', 'INCOMPLETE'}:
        retryable = bool(pipeline.get('retryable'))
        code = pipeline.get('last_error')
        label = 'Moj Elektro še nima vseh podatkov za mesec.'
        if stage == 'ERROR':
            label = 'Napaka pri samodejni obdelavi računa.'
            if code == 'moj_elektro_auth':
                label = 'Prijava v Moj Elektro ni uspela. Preveri nastavitve integracije.'
        result.update(step=2, level='error' if stage == 'ERROR' else 'warning',
                      terminal=not retryable, label=label, error_code=code,
                      next_attempt_at=pipeline.get('next_attempt_at') if retryable else None)
    return result
