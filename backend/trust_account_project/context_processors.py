from apps.settings.models import LawFirm


def law_firm_context(request):
    """Add law firm information to all template contexts"""
    return {
        'global_law_firm': LawFirm.get_active_firm()
    }